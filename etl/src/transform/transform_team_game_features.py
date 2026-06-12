from sqlalchemy import create_engine, text

def transform_team_game_features(database_url):
    engine = create_engine(database_url)
    result = None

    query = text("""
    SELECT  id, 
            game_date,
            home_team,
            away_team,
            home_score,
            away_score,
            spread_home,
            spread_away
    FROM games
    WHERE home_score IS NOT NULL AND away_score IS NOT NULL
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        games = result.mappings().all()  # Convert to list of dicts

    team_game_rows = []
    for game in games:
        home_team = game["home_team"]
        away_team = game["away_team"]
        home_score = game["home_score"]
        away_score = game["away_score"]
        spread_home = game["spread_home"]
        spread_away = game["spread_away"]
        home_favorite = spread_home is not None and spread_home < 0
        home_covered = (home_score - away_score) + spread_home > 0
        home_spread_diff = (home_score - away_score) + spread_home if spread_home is not None else None

        # Home team row
        team_game_rows.append({
            "game_id":game["id"],
            "team": home_team,
            "opponent_team": away_team,
            "is_home": True,
            "team_score": home_score,
            "opponent_score": away_score,
            "point_diff": home_score - away_score,
            "is_favorite": home_favorite,
            "spread": spread_home,
            "covered_spread": home_covered,
            "spread_diff": home_spread_diff,
            "game_date": game["game_date"]
        })

        # Away team row
        team_game_rows.append({
            "game_id": game["id"],
            "team": away_team,
            "opponent_team": home_team,
            "is_home": False,
            "team_score": away_score,
            "opponent_score": home_score,
            "point_diff": away_score - home_score,
            "is_favorite": not home_favorite,
            "covered_spread": not home_covered,
            "spread": spread_away,
            "spread_diff": -home_spread_diff,
            "game_date": game["game_date"]
        })

    return team_game_rows

    
    