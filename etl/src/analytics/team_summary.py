from sqlalchemy import create_engine, text


TEAM_RECORD_SUMMARY_SQL = """
SELECT
    team,
    COUNT(*) AS games_played,
    SUM(CASE WHEN point_diff > 0 THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN point_diff < 0 THEN 1 ELSE 0 END) AS losses,
    ROUND(AVG(point_diff), 2) AS avg_point_diff,
    ROUND(AVG(team_score), 2) AS avg_points_for,
    ROUND(AVG(opponent_score), 2) AS avg_points_against,
    ROUND(AVG(recent_avg_margin), 2) AS avg_recent_margin,
    ROUND(AVG(recent_win_pct), 3) AS avg_recent_win_pct
FROM team_game_features
WHERE team_score IS NOT NULL
  AND opponent_score IS NOT NULL
  AND team = :team
GROUP BY team
ORDER BY wins DESC, avg_point_diff DESC;
"""

TEAM_HOME_AWAY_SUMMARY_SQL = """
SELECT
    team,
    CASE WHEN is_home THEN 'home' ELSE 'away' END AS location,
    COUNT(*) AS games_played,
    SUM(CASE WHEN point_diff > 0 THEN 1 ELSE 0 END) AS wins,
    ROUND(AVG(point_diff), 2) AS avg_point_diff,
    ROUND(AVG(team_score), 2) AS avg_points_for,
    ROUND(AVG(opponent_score), 2) AS avg_points_against
FROM team_game_features
WHERE team_score IS NOT NULL
  AND opponent_score IS NOT NULL
  AND team = :team
GROUP BY team, location
ORDER BY team, location;
"""

TEAM_RECENT_FORM_SQL = """
SELECT
    team,
    game_date,
    opponent_team,
    is_home,
    team_score,
    opponent_score,
    point_diff,
    rest_days,
    recent_avg_margin,
    recent_win_pct,
    spread,
    covered_spread,
    spread_diff
FROM team_game_features
WHERE team_score IS NOT NULL
  AND opponent_score IS NOT NULL
  AND team = :team
ORDER BY game_date DESC
LIMIT 10;
"""


def get_team_record_summary(database_url, team):
    engine = create_engine(database_url)
    return _fetch_all(engine, TEAM_RECORD_SUMMARY_SQL, {"team": team})


def get_team_home_away_summary(database_url, team):
    engine = create_engine(database_url)
    return _fetch_all(engine, TEAM_HOME_AWAY_SUMMARY_SQL, {"team": team})


def get_team_recent_form(database_url, team):
    engine = create_engine(database_url)
    return _fetch_all(engine, TEAM_RECENT_FORM_SQL, {"team": team})


def get_team_summary_data(database_url, team):
    engine = create_engine(database_url)
    params = {"team": team}

    return {
        "team": team,
        "record_summary": _fetch_all(engine, TEAM_RECORD_SUMMARY_SQL, params),
        "home_away_summary": _fetch_all(engine, TEAM_HOME_AWAY_SUMMARY_SQL, params),
        "recent_form": _fetch_all(engine, TEAM_RECENT_FORM_SQL, params),
    }


def _fetch_all(engine, query, params=None):
    with engine.connect() as connection:
        rows = connection.execute(text(query), params or {}).mappings().all()

    return [dict(row) for row in rows]
