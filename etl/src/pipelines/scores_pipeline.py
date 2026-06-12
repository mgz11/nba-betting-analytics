import logging
from src.ingest.fetch_scores_api import fetch_scores_from_api
from src.transform.transform_scores import transform_scores
from src.load.update_scores import update_scores
from config.env import DATABASE_URL

logger = logging.getLogger(__name__)

def run_scores_pipeline():
    # Step 1: Fetch scores from API
    logger.info("Starting scores pipeline...")
    api_scores = fetch_scores_from_api()
    if not api_scores:
        logger.warning("No scores data fetched from API.")
        return

    # Step 2: Transform scores data
    logger.info("Transforming scores data...")
    transformed_scores = transform_scores(api_scores)
    logger.info(f"Transformed {len(transformed_scores)} scores.")

    # Step 3: Update scores in PostgreSQL
    logger.info("Updating scores in PostgreSQL...")
    update_scores(DATABASE_URL, transformed_scores)
    logger.info("Scores updated in PostgreSQL successfully.")