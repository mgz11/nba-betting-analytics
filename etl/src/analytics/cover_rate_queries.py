from sqlalchemy import create_engine, text


COVER_RATE_BY_TEAM_SQL = """
SELECT
    team,
    COUNT(*) AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END) AS covers,
    SUM(CASE WHEN covered_spread = FALSE THEN 1 ELSE 0 END) AS non_covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3) AS cover_rate,
    ROUND(AVG(spread_diff), 2) AS avg_spread_diff
FROM team_game_features
WHERE covered_spread IS NOT NULL
GROUP BY team
ORDER BY cover_rate DESC, games_with_spread DESC;
"""

COVER_RATE_BY_HOME_AWAY_SQL = """
SELECT
    CASE WHEN is_home THEN 'home' ELSE 'away' END AS location,
    COUNT(*) AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END) AS covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3) AS cover_rate,
    ROUND(AVG(spread_diff), 2) AS avg_spread_diff
FROM team_game_features
WHERE covered_spread IS NOT NULL
GROUP BY location
ORDER BY location;
"""

COVER_RATE_BY_FAVORITE_STATUS_SQL = """
SELECT
    CASE
        WHEN is_favorite THEN 'favorite'
        ELSE 'underdog'
    END AS favorite_status,
    COUNT(*) AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END) AS covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3) AS cover_rate,
    ROUND(AVG(spread_diff), 2) AS avg_spread_diff
FROM team_game_features
WHERE covered_spread IS NOT NULL
  AND is_favorite IS NOT NULL
GROUP BY favorite_status
ORDER BY favorite_status;
"""

COVER_RATE_BY_TEAM_AND_LOCATION_SQL = """
SELECT
    team,
    CASE WHEN is_home THEN 'home' ELSE 'away' END AS location,
    COUNT(*) AS games_with_spread,
    SUM(CASE WHEN covered_spread THEN 1 ELSE 0 END) AS covers,
    ROUND(AVG(CASE WHEN covered_spread THEN 1.0 ELSE 0.0 END), 3) AS cover_rate,
    ROUND(AVG(spread_diff), 2) AS avg_spread_diff
FROM team_game_features
WHERE covered_spread IS NOT NULL
GROUP BY team, location
ORDER BY team, location;
"""


def get_cover_rate_by_team(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, COVER_RATE_BY_TEAM_SQL)


def get_cover_rate_by_home_away(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, COVER_RATE_BY_HOME_AWAY_SQL)


def get_cover_rate_by_favorite_status(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, COVER_RATE_BY_FAVORITE_STATUS_SQL)


def get_cover_rate_by_team_and_location(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, COVER_RATE_BY_TEAM_AND_LOCATION_SQL)


def get_cover_rate_data(database_url):
    engine = create_engine(database_url)

    return {
        "by_team": _fetch_all(engine, COVER_RATE_BY_TEAM_SQL),
        "by_home_away": _fetch_all(engine, COVER_RATE_BY_HOME_AWAY_SQL),
        "by_favorite_status": _fetch_all(
            engine, COVER_RATE_BY_FAVORITE_STATUS_SQL
        ),
        "by_team_and_location": _fetch_all(
            engine, COVER_RATE_BY_TEAM_AND_LOCATION_SQL
        ),
    }


def _fetch_all(engine, query):
    with engine.connect() as connection:
        rows = connection.execute(text(query)).mappings().all()

    return [dict(row) for row in rows]
