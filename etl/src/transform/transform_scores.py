def transform_scores(raw_games):
    rows = []

    for game in raw_games:
        game_id = game["id"]
        home_team = game["home_team"]
        away_team = game["away_team"]

        # Skip games with no scores
        if not game["scores"]:
            continue

        # Skip games that are not final
        if not game["completed"]:
            continue

        home_score = None
        away_score = None

        for score in game["scores"]:
            if score["name"] == home_team:
                home_score = int(score["score"])
            elif score["name"] == away_team:
                away_score = int(score["score"])

        # Only include games where we have both scores
        if home_score is None or away_score is None:
            continue

        rows.append({
            "external_game_id": game_id,
            "home_score": home_score,
            "away_score": away_score
        })

    return rows