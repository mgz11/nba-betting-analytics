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
SELECT
    COUNT(*) AS games_with_lines,
    ROUND(AVG(spread_home), 2) AS avg_home_spread,
    ROUND(AVG(spread_away), 2) AS avg_away_spread,
    ROUND(AVG(total), 2) AS avg_total_line,
    ROUND(AVG(moneyline_home), 2) AS avg_home_moneyline,
    ROUND(AVG(moneyline_away), 2) AS avg_away_moneyline
FROM games
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
    return _fetch_all(engine, LEAGUE_SCORING_SUMMARY_SQL)


def get_league_betting_market_summary(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, LEAGUE_BETTING_MARKET_SUMMARY_SQL)


def get_league_results_by_date(database_url):
    engine = create_engine(database_url)
    return _fetch_all(engine, LEAGUE_RESULTS_BY_DATE_SQL)


def get_league_summary_data(database_url):
    engine = create_engine(database_url)

    return {
        "scoring_summary": _fetch_all(engine, LEAGUE_SCORING_SUMMARY_SQL),
        "betting_market_summary": _fetch_all(
            engine, LEAGUE_BETTING_MARKET_SUMMARY_SQL
        ),
        "results_by_date": _fetch_all(engine, LEAGUE_RESULTS_BY_DATE_SQL),
    }


def _fetch_all(engine, query):
    with engine.connect() as connection:
        rows = connection.execute(text(query)).mappings().all()

    return [dict(row) for row in rows]
