from sqlalchemy import create_engine, text

WINDOW_SIZE = 5
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
    ORDER BY game_date
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        games = result.mappings().all()  # Convert to list of dicts

    team_game_rows = []
    team_history = {}
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

        # Calculate rolling statisctics for home team
        previous_home_games = team_history.get(home_team, [])
        previous_away_games = team_history.get(away_team, [])
        home_rest, home_avg_margin, home_win_pct = calculate_rolling_stats(game["game_date"], previous_home_games)
        away_rest, away_avg_margin, away_win_pct = calculate_rolling_stats(game["game_date"], previous_away_games)

        # Home team row
        team_game_rows.append({
            "game_id":game["id"],
            "team": home_team,
            "opponent_team": away_team,
            "is_home": True,
            "team_score": home_score,
            "opponent_score": away_score,
            "point_diff": home_score - away_score,
            "rest_days": home_rest,
            "recent_avg_margin": home_avg_margin,
            "recent_win_pct": home_win_pct,
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
            "rest_days": away_rest,
            "recent_avg_margin": away_avg_margin,
            "recent_win_pct": away_win_pct,
            "is_favorite": not home_favorite,
            "covered_spread": not home_covered,
            "spread": spread_away,
            "spread_diff": -home_spread_diff,
            "game_date": game["game_date"]
        })

         # Update team history with current game
        if home_team not in team_history:
            team_history[home_team] = []
        team_history[home_team].append({
            "game_date": game["game_date"],
            "point_diff": home_score - away_score,
            "win": home_score > away_score
        })
        if away_team not in team_history:
            team_history[away_team] = []
        team_history[away_team].append({
            "game_date": game["game_date"],
            "point_diff": away_score - home_score,
            "win": away_score > home_score
        })

    return team_game_rows

def calculate_rolling_stats(game_date, team_history):
    recent_games = team_history[-WINDOW_SIZE:] if team_history else []
    rest_days = (game_date - team_history[-1]["game_date"]).days if team_history else None
    recent_avg_margin = (sum(g["point_diff"] for g in recent_games) / len(recent_games)) if recent_games else None
    recent_win_pct = (sum(1 for g in recent_games if g["win"]) / len(recent_games)) if recent_games else None

    return rest_days, recent_avg_margin, recent_win_pct
