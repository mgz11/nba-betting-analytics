from sqlalchemy import create_engine, text

def load_games(database_url, rows):
    engine = create_engine(database_url)

    query = text("""
    INSERT INTO games (
        external_game_id,
        game_date,
        home_team,
        away_team,
        spread_home,
        spread_away,
        moneyline_home,
        moneyline_away,
        total)
    VALUES (
        :external_game_id,
        :game_date,
        :home_team,
        :away_team,
        :spread_home,
        :spread_away,
        :moneyline_home,
        :moneyline_away,
        :total)
    ON CONFLICT (external_game_id)
    DO UPDATE SET
        spread_home = EXCLUDED.spread_home,
        spread_away = EXCLUDED.spread_away,
        moneyline_home = EXCLUDED.moneyline_home,
        moneyline_away = EXCLUDED.moneyline_away,
        total = EXCLUDED.total
    """)

    with engine.begin() as connection:
        connection.execute(query, rows)