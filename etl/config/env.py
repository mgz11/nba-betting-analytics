import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

ENV = os.getenv("ENV")
DATABASE_URL = os.getenv("DATABASE_URL")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")
ODDS_API_BASE_URL = os.getenv("ODDS_API_BASE_URL")
BASE_URL = os.getenv("BASE_URL")