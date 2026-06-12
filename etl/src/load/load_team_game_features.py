from sqlalchemy import create_engine, text

def load_team_game_features(database_url, rows):
    engine = create_engine(database_url)

    query = text("""
    INSERT INTO team_game_features (
        game_id,
        team,
        opponent_team,
        is_home,
        team_score,
        opponent_score,
        point_diff,
        is_favorite,
        spread,
        covered_spread,
        spread_diff,
        game_date
    ) VALUES (
        :game_id,
        :team,
        :opponent_team,
        :is_home,
        :team_score,
        :opponent_score,
        :point_diff,
        :is_favorite,
        :spread,
        :covered_spread,
        :spread_diff,
        :game_date
    ) ON CONFLICT (game_id, team) DO UPDATE
    SET 
        opponent_team = EXCLUDED.opponent_team,
        is_home = EXCLUDED.is_home,
        team_score = EXCLUDED.team_score,
        opponent_score = EXCLUDED.opponent_score,
        point_diff = EXCLUDED.point_diff,
        is_favorite = EXCLUDED.is_favorite,
        spread = EXCLUDED.spread,
        covered_spread = EXCLUDED.covered_spread,
        spread_diff = EXCLUDED.spread_diff,
        game_date = EXCLUDED.game_date
    """)

    with engine.begin() as connection:
        connection.execute(query, rows)