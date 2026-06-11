import json
from config.env import DATABASE_URL
from config.settings import ODDS_RAW_DIR
from src.ingest.fetch_odds_api import fetch_odds_from_api
from src.ingest.fetch_scores_api import fetch_scores_from_api
from src.ingest.load_local_odds import load_local_odds
from src.transform.transform_odds import transform_odds
from src.transform.transform_scores import transform_scores
from src.load.load_postgres import load_games
from src.load.update_scores import update_scores
from datetime import datetime

def main():
    # # Step 1: Fetch odds data from API
    # print("Fetching odds data from API...")
    # api_odds = fetch_odds_from_api()
    # if not api_odds:
    #     print("No odds data fetched from API.")
    #     return
    
    # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # raw_path = ODDS_RAW_DIR / f"odds_{timestamp}.json"

    # # Step 2: Save raw API data locally
    # print(f"Saving raw API data to {raw_path}...")
    # raw_path.parent.mkdir(parents=True, exist_ok=True)

    # with open(raw_path, "w") as f:
    #     import json
    #     json.dump(api_odds, f, indent=2)

    # print(f"Saved {len(api_odds)} games to {raw_path}")

    # '''
    # TESTING TRANSFORMED ROWS
    # '''
    # with open(ODDS_RAW_DIR / "odds_20260609_142500.json") as f:
    #     raw_odds = json.load(f) 
    # transformed_rows = transform_odds(raw_odds)
    # print(f"Transformed {len(transformed_rows)} games for loading.")
    # print(transformed_rows)
    # load_games(DATABASE_URL, transformed_rows)
    # print("Data loaded into PostgreSQL successfully.")

    # Step 3: Fetch scores data from API
    print("Fetching scores data from API...")
    api_scores = fetch_scores_from_api()
    if not api_scores:
        print("No scores data fetched from API.")
        return

    # Step 4: Transform scores data
    print("Transforming scores data...")
    transformed_scores = transform_scores(api_scores)
    
    # Step 5: Update scores in PostgreSQL
    print("Updating scores in PostgreSQL...")
    update_scores(DATABASE_URL, transformed_scores)
    print("Scores updated in PostgreSQL successfully.")

if __name__ == "__main__":
    main()