import pool from "@/lib/db";

const coverRateByTeamQuery = `
  SELECT
    team,
    COUNT(*)::integer AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END)::integer AS covers,
    SUM(CASE WHEN covered_spread = FALSE THEN 1 ELSE 0 END)::integer AS non_covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3)::double precision AS cover_rate,
    ROUND(AVG(spread_diff), 2)::double precision AS avg_spread_diff
  FROM team_game_features
  WHERE covered_spread IS NOT NULL
  GROUP BY team
  ORDER BY cover_rate DESC, games_with_spread DESC
`;

const coverRateByHomeAwayQuery = `
  SELECT
    CASE WHEN is_home THEN 'home' ELSE 'away' END AS location,
    COUNT(*)::integer AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END)::integer AS covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3)::double precision AS cover_rate,
    ROUND(AVG(spread_diff), 2)::double precision AS avg_spread_diff
  FROM team_game_features
  WHERE covered_spread IS NOT NULL
  GROUP BY location
  ORDER BY location
`;

const coverRateByFavoriteStatusQuery = `
  SELECT
    CASE WHEN is_favorite THEN 'favorite' ELSE 'underdog' END AS favorite_status,
    COUNT(*)::integer AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END)::integer AS covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3)::double precision AS cover_rate,
    ROUND(AVG(spread_diff), 2)::double precision AS avg_spread_diff
  FROM team_game_features
  WHERE covered_spread IS NOT NULL
    AND is_favorite IS NOT NULL
  GROUP BY favorite_status
  ORDER BY favorite_status
`;

const coverRateByTeamAndLocationQuery = `
  SELECT
    team,
    CASE WHEN is_home THEN 'home' ELSE 'away' END AS location,
    COUNT(*)::integer AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END)::integer AS covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3)::double precision AS cover_rate,
    ROUND(AVG(spread_diff), 2)::double precision AS avg_spread_diff
  FROM team_game_features
  WHERE covered_spread IS NOT NULL
  GROUP BY team, location
  ORDER BY team, location
`;

export async function getCoverRateByTeam() {
  return (await pool.query(coverRateByTeamQuery)).rows;
}

export async function getCoverRateByHomeAway() {
  return (await pool.query(coverRateByHomeAwayQuery)).rows;
}

export async function getCoverRateByFavoriteStatus() {
  return (await pool.query(coverRateByFavoriteStatusQuery)).rows;
}

export async function getCoverRateByTeamAndLocation() {
  return (await pool.query(coverRateByTeamAndLocationQuery)).rows;
}

export async function getCoverRateData() {
  const [byTeam, byHomeAway, byFavoriteStatus, byTeamAndLocation] =
    await Promise.all([
      getCoverRateByTeam(),
      getCoverRateByHomeAway(),
      getCoverRateByFavoriteStatus(),
      getCoverRateByTeamAndLocation(),
    ]);

  return {
    by_team: byTeam,
    by_home_away: byHomeAway,
    by_favorite_status: byFavoriteStatus,
    by_team_and_location: byTeamAndLocation,
  };
}
