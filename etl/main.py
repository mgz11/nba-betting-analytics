from config.env import DATABASE_URL
from config.settings import ODDS_RAW_DIR
from src.ingest.load_local_odds import load_local_odds
from src.transform.transform_odds import transform_odds
from src.load.load_postgres import load_games

def main():
    raw_path = ODDS_RAW_DIR / "sample_odds.json"

    raw_games = load_local_odds(raw_path)
    transformed_games = transform_odds(raw_games)
    load_games(DATABASE_URL, transformed_games)

    print(f"Successfully loaded {len(transformed_games)} games into the database.")

if __name__ == "__main__":
    main()