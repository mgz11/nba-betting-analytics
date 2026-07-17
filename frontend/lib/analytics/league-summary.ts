import pool from "@/lib/db";

const leagueScoringSummaryQuery = `
  SELECT
    COUNT(*)::integer AS games_played,
    ROUND(AVG(home_score + away_score), 2)::double precision AS avg_total_points,
    ROUND(AVG(home_score), 2)::double precision AS avg_home_points,
    ROUND(AVG(away_score), 2)::double precision AS avg_away_points,
    ROUND(AVG(home_score - away_score), 2)::double precision AS avg_home_margin,
    SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END)::integer AS home_wins,
    SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END)::integer AS away_wins
  FROM games
  WHERE home_score IS NOT NULL
    AND away_score IS NOT NULL
`;

const leagueBettingMarketSummaryQuery = `
  WITH betting_markets AS (
    SELECT
      games.*,
      CASE
        WHEN moneyline_home < moneyline_away THEN 'home'
        WHEN moneyline_away < moneyline_home THEN 'away'
      END AS favorite_side,
      CASE
        WHEN moneyline_home < moneyline_away THEN moneyline_home
        WHEN moneyline_away < moneyline_home THEN moneyline_away
      END AS favorite_decimal_odds
    FROM games
  )
  SELECT
    COUNT(*)::integer AS games_with_lines,
    ROUND(AVG(spread_home), 2)::double precision AS avg_home_spread,
    ROUND(AVG(spread_away), 2)::double precision AS avg_away_spread,
    ROUND(AVG(total), 2)::double precision AS avg_total_line,
    COUNT(*) FILTER (WHERE favorite_side = 'home')::integer AS home_favorites,
    COUNT(*) FILTER (WHERE favorite_side = 'away')::integer AS away_favorites,
    ROUND(AVG(favorite_decimal_odds), 3)::double precision AS avg_favorite_decimal_odds,
    ROUND(AVG(1.0 / NULLIF(favorite_decimal_odds, 0)), 4)::double precision
      AS avg_implied_probability,
    ROUND(AVG(
      CASE
        WHEN home_score IS NULL OR away_score IS NULL OR favorite_side IS NULL THEN NULL
        WHEN favorite_side = 'home' AND home_score > away_score THEN 1.0
        WHEN favorite_side = 'away' AND away_score > home_score THEN 1.0
        ELSE 0.0
      END
    ), 4)::double precision AS favorite_win_rate
  FROM betting_markets
  WHERE spread_home IS NOT NULL
     OR spread_away IS NOT NULL
     OR total IS NOT NULL
     OR moneyline_home IS NOT NULL
     OR moneyline_away IS NOT NULL
`;

const leagueResultsByDateQuery = `
  SELECT
    game_date::text AS game_date,
    COUNT(*)::integer AS games_played,
    ROUND(AVG(home_score + away_score), 2)::double precision AS avg_total_points,
    ROUND(AVG(home_score - away_score), 2)::double precision AS avg_home_margin,
    SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END)::integer AS home_wins,
    SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END)::integer AS away_wins
  FROM games
  WHERE home_score IS NOT NULL
    AND away_score IS NOT NULL
  GROUP BY game_date
  ORDER BY game_date DESC
`;

export async function getLeagueScoringSummary() {
  return (await pool.query(leagueScoringSummaryQuery)).rows[0] ?? null;
}

export async function getLeagueBettingMarketSummary() {
  return (await pool.query(leagueBettingMarketSummaryQuery)).rows[0] ?? null;
}

export async function getLeagueResultsByDate() {
  return (await pool.query(leagueResultsByDateQuery)).rows;
}

export async function getLeagueSummaryData() {
  const [scoringSummary, bettingMarketSummary, resultsByDate] = await Promise.all([
    getLeagueScoringSummary(),
    getLeagueBettingMarketSummary(),
    getLeagueResultsByDate(),
  ]);

  return {
    scoring_summary: scoringSummary,
    betting_market_summary: bettingMarketSummary,
    results_by_date: resultsByDate,
  };
}
