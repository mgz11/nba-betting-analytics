import logging
from src.transform.transform_team_game_features import transform_team_game_features
from src.load.load_team_game_features import load_team_game_features
from src.validate.team_game_features import validate_team_game_features
from config.env import DATABASE_URL

logger = logging.getLogger(__name__)

def run_team_features_pipeline():
    # Step 1: Transform team game features
    logger.info("Starting team game features pipeline...")
    team_game_features = transform_team_game_features(DATABASE_URL)
    logger.info(f"Transformed {len(team_game_features)} team game feature rows.")

    # Step 2: Load team game features into PostgreSQL
    logger.info("Loading team game features into PostgreSQL...")
    load_team_game_features(DATABASE_URL, team_game_features)
    logger.info("Team game features loaded into PostgreSQL successfully.")

    # Step 3: Validate persisted team game features
    logger.info("Validating team game features...")
    validate_team_game_features(DATABASE_URL)
    logger.info("Team game features validated successfully.")
