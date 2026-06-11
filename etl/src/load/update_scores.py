from sqlalchemy import create_engine, text

def update_scores(database_url, rows):
    engine = create_engine(database_url)

    query = text("""
    UPDATE games
    SET home_score = :home_score,
        away_score = :away_score
    WHERE external_game_id = :external_game_id
    """)

    with engine.begin() as connection:
        connection.execute(query, rows)