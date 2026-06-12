import logging
from src.pipelines.odds_pipeline import run_odds_pipeline
from src.pipelines.scores_pipeline import run_scores_pipeline
from src.pipelines.team_features_pipeline import run_team_features_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting ETL process...")

    # Run odds pipeline to fetch and load the latest odds data
    # run_odds_pipeline()
    
    # Run scores pipeline to fetch and update the latest scores in the database
    # run_scores_pipeline()
    
    # Run team features pipeline to update features based on the latest scores
    run_team_features_pipeline()
    
    logger.info("ETL process completed successfully.")
    

if __name__ == "__main__":
    main()