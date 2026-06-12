import logging
import json
from src.ingest.fetch_odds_api import fetch_odds_from_api
from src.ingest.load_local_odds import load_local_odds
from src.transform.transform_odds import transform_odds
from src.load.load_postgres import load_games
from config.env import DATABASE_URL
from config.settings import ODDS_RAW_DIR
from datetime import datetime

logger = logging.getLogger(__name__)

def run_odds_pipeline():
    # Step 1: Fetch odds from API
    logger.info("Starting odds pipeline...")
    api_odds = fetch_odds_from_api()
    if not api_odds:
        logger.warning("No odds data fetched from API.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = ODDS_RAW_DIR / f"odds_{timestamp}.json"

    # Step 2: Save raw API data locally
    logger.info(f"Saving raw API data to {raw_path}...")
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    with open(raw_path, "w") as f:
        json.dump(api_odds, f, indent=2)

    logger.info(f"Saved {len(api_odds)} games to {raw_path}")

    # Step 3: Transform odds data
    logger.info("Transforming odds data...")
    transformed_rows = transform_odds(api_odds)
    logger.info(f"Transformed {len(transformed_rows)} games for loading.")

    # Step 4: Load transformed data into PostgreSQL
    logger.info("Loading transformed odds data into PostgreSQL...")
    load_games(DATABASE_URL, transformed_rows)
    logger.info("Transformed odds data loaded into PostgreSQL successfully.")