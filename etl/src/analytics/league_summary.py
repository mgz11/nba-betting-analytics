from sqlalchemy import create_engine, text


LEAGUE_SCORING_SUMMARY_SQL = """
SELECT
    COUNT(*) AS games_played,
    ROUND(AVG(home_score + away_score), 2) AS avg_total_points,
    ROUND(AVG(home_score), 2) AS avg_home_points,
    ROUND(AVG(away_score), 2) AS avg_away_points,
    ROUND(AVG(home_score - away_score), 2) AS avg_home_margin,
    SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END) AS away_wins
FROM games
WHERE home_score IS NOT NULL
  AND away_score IS NOT NULL;
"""

LEAGUE_BETTING_MARKET_SUMMARY_SQL = """
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
    COUNT(*) AS games_with_lines,
    ROUND(AVG(spread_home), 2) AS avg_home_spread,
    ROUND(AVG(spread_away), 2) AS avg_away_spread,
    ROUND(AVG(total), 2) AS avg_total_line,
    COUNT(*) FILTER (WHERE favorite_side = 'home') AS home_favorites,
    COUNT(*) FILTER (WHERE favorite_side = 'away') AS away_favorites,
    ROUND(AVG(favorite_decimal_odds), 3) AS avg_favorite_decimal_odds,
    ROUND(AVG(1.0 / NULLIF(favorite_decimal_odds, 0)), 4)
        AS avg_implied_probability,
    ROUND(AVG(
        CASE
            WHEN home_score IS NULL OR away_score IS NULL OR favorite_side IS NULL
                THEN NULL
            WHEN favorite_side = 'home' AND home_score > away_score THEN 1.0
            WHEN favorite_side = 'away' AND away_score > home_score THEN 1.0
            ELSE 0.0
        END
    ), 4) AS favorite_win_rate
FROM betting_markets
WHERE spread_home IS NOT NULL
   OR spread_away IS NOT NULL
   OR total IS NOT NULL
   OR moneyline_home IS NOT NULL
   OR moneyline_away IS NOT NULL;
"""

LEAGUE_RESULTS_BY_DATE_SQL = """
SELECT
    game_date,
    COUNT(*) AS games_played,
    ROUND(AVG(home_score + away_score), 2) AS avg_total_points,
    ROUND(AVG(home_score - away_score), 2) AS avg_home_margin,
    SUM(CASE WHEN home_score > away_score THEN 1 ELSE 0 END) AS home_wins,
    SUM(CASE WHEN away_score > home_score THEN 1 ELSE 0 END) AS away_wins
FROM games
WHERE home_score IS NOT NULL
  AND away_score IS NOT NULL
GROUP BY game_date
ORDER BY game_date DESC;
"""


def get_league_scoring_summary(database_url):
    engine = create_engine(database_url)
    return _fetch_one(engine, LEAGUE_SCORING_SUMMARY_SQL)


def get_league_betting_market_summary(database_url):
    engine = create_engine(database_url)
    return _fetch_one(engine, LEAGUE_BETTING_MARKET_SUMMARY_SQL)


def get_league_results_by_date(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, LEAGUE_RESULTS_BY_DATE_SQL)


def get_league_summary_data(database_url):
    engine = create_engine(database_url)

    return {
        "scoring_summary": _fetch_one(engine, LEAGUE_SCORING_SUMMARY_SQL),
        "betting_market_summary": _fetch_one(
            engine, LEAGUE_BETTING_MARKET_SUMMARY_SQL
        ),
        "results_by_date": _fetch_all(engine, LEAGUE_RESULTS_BY_DATE_SQL),
    }


def _fetch_one(engine, query):
    rows = _fetch_all(engine, query)
    return rows[0] if rows else None


def _fetch_all(engine, query):
    with engine.connect() as connection:
        rows = connection.execute(text(query)).mappings().all()

    return [dict(row) for row in rows]
