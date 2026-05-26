from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

ODDS_RAW_DIR = RAW_DIR / "odds"
NBA_RAW_DIR = RAW_DIR / "nba"