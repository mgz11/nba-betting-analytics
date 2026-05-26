from datetime import datetime

def transform_odds(raw_games):
    rows = []

    for game in raw_games:
        game_id = game["id"]
        game_date = datetime.fromisoformat(
            game["commence_time"].replace("Z", "+00:00")
        ).date()

        home_team = game["home_team"]
        away_team = game["away_team"]

        spread_home = None
        spread_away = None
        moneyline_home = None
        moneyline_away = None
        total = None

        bookmaker = game["bookmakers"][0] if game["bookmakers"] else None

        for market in bookmaker["markets"]:
            if market["key"] == "spreads":
                for outcome in market["outcomes"]:
                    if outcome["name"] == home_team:
                        spread_home = outcome["point"]
                    elif outcome["name"] == away_team:
                        spread_away = outcome["point"]

            if market["key"] == "h2h":
                for outcome in market["outcomes"]:
                    if outcome["name"] == home_team:
                        moneyline_home = outcome["price"]
                    elif outcome["name"] == away_team:
                        moneyline_away = outcome["price"]

            if market["key"] == "totals":
                total = market["outcomes"][0]["point"]

        rows.append({
            "external_game_id": game_id,
            "game_date": game_date,
            "home_team": home_team,
            "away_team": away_team, 
            "spread_home": spread_home,
            "spread_away": spread_away,
            "moneyline_home": moneyline_home,
            "moneyline_away": moneyline_away,
            "total": total
        })

    return rows
