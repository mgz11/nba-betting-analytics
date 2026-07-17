import pool from "@/lib/db";

const teamRecordSummaryQuery = `
  SELECT
    team,
    COUNT(*)::integer AS games_played,
    SUM(CASE WHEN point_diff > 0 THEN 1 ELSE 0 END)::integer AS wins,
    SUM(CASE WHEN point_diff < 0 THEN 1 ELSE 0 END)::integer AS losses,
    ROUND(AVG(point_diff), 2)::double precision AS avg_point_diff,
    ROUND(AVG(team_score), 2)::double precision AS avg_points_for,
    ROUND(AVG(opponent_score), 2)::double precision AS avg_points_against,
    ROUND(AVG(recent_avg_margin), 2)::double precision AS avg_recent_margin,
    ROUND(AVG(recent_win_pct), 3)::double precision AS avg_recent_win_pct
  FROM team_game_features
  WHERE team_score IS NOT NULL
    AND opponent_score IS NOT NULL
    AND team = $1
  GROUP BY team
  ORDER BY wins DESC, avg_point_diff DESC
`;

const teamHomeAwaySummaryQuery = `
  SELECT
    team,
    CASE WHEN is_home THEN 'home' ELSE 'away' END AS location,
    COUNT(*)::integer AS games_played,
    SUM(CASE WHEN point_diff > 0 THEN 1 ELSE 0 END)::integer AS wins,
    ROUND(AVG(point_diff), 2)::double precision AS avg_point_diff,
    ROUND(AVG(team_score), 2)::double precision AS avg_points_for,
    ROUND(AVG(opponent_score), 2)::double precision AS avg_points_against
  FROM team_game_features
  WHERE team_score IS NOT NULL
    AND opponent_score IS NOT NULL
    AND team = $1
  GROUP BY team, location
  ORDER BY team, location
`;

const teamRecentFormQuery = `
  SELECT
    team,
    game_date::text AS game_date,
    opponent_team,
    is_home,
    team_score,
    opponent_score,
    point_diff,
    rest_days,
    recent_avg_margin::double precision AS recent_avg_margin,
    recent_win_pct::double precision AS recent_win_pct,
    spread::double precision AS spread,
    covered_spread,
    spread_diff::double precision AS spread_diff
  FROM team_game_features
  WHERE team_score IS NOT NULL
    AND opponent_score IS NOT NULL
    AND team = $1
  ORDER BY game_date DESC
  LIMIT 10
`;

export async function getTeamRecordSummary(team: string) {
  return (await pool.query(teamRecordSummaryQuery, [team])).rows;
}

export async function getTeamHomeAwaySummary(team: string) {
  return (await pool.query(teamHomeAwaySummaryQuery, [team])).rows;
}

export async function getTeamRecentForm(team: string) {
  return (await pool.query(teamRecentFormQuery, [team])).rows;
}

export async function getTeamSummaryData(team: string) {
  const [recordSummary, homeAwaySummary, recentForm] = await Promise.all([
    getTeamRecordSummary(team),
    getTeamHomeAwaySummary(team),
    getTeamRecentForm(team),
  ]);

  return {
    team,
    record_summary: recordSummary,
    home_away_summary: homeAwaySummary,
    recent_form: recentForm,
  };
}
