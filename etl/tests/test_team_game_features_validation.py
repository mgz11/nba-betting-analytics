import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, text

ETL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ETL_ROOT))

from src.load.load_team_game_features import load_team_game_features
from src.transform.transform_team_game_features import transform_team_game_features
from src.validate.team_game_features import (
    TeamGameFeaturesValidationError,
    validate_completed_games_have_two_team_rows,
    validate_rolling_stats,
    validate_team_game_features,
)


class TeamGameFeaturesValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_url = f"sqlite:///{Path(self.temp_dir.name) / 'test.db'}"
        self.engine = create_engine(self.database_url)
        self._create_schema()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validates_two_rows_per_completed_game_and_rolling_stats(self):
        self._insert_games([
            {
                "id": 1,
                "external_game_id": "game-1",
                "game_date": date(2026, 1, 1),
                "home_team": "Aces",
                "away_team": "Bears",
                "home_score": 90,
                "away_score": 80,
                "spread_home": -4.5,
                "spread_away": 4.5,
            },
            {
                "id": 2,
                "external_game_id": "game-2",
                "game_date": date(2026, 1, 3),
                "home_team": "Cats",
                "away_team": "Aces",
                "home_score": 70,
                "away_score": 75,
                "spread_home": None,
                "spread_away": None,
            },
            {
                "id": 3,
                "external_game_id": "game-3",
                "game_date": date(2026, 1, 5),
                "home_team": "Bears",
                "away_team": "Cats",
                "home_score": 88,
                "away_score": 81,
                "spread_home": 1.5,
                "spread_away": -1.5,
            },
        ])

        rows = transform_team_game_features(self.database_url)
        load_team_game_features(self.database_url, rows)

        results = validate_team_game_features(self.database_url)
        self.assertEqual(
            [result.name for result in results],
            [
                "completed_games_have_two_team_rows",
                "rolling_stats_match_expected_values",
            ],
        )

        with self.engine.connect() as connection:
            aces_game_2 = connection.execute(
                text("""
                SELECT rest_days, recent_avg_margin, recent_win_pct
                FROM team_game_features
                WHERE game_id = 2 AND team = 'Aces'
                """)
            ).mappings().one()
            cats_game_3 = connection.execute(
                text("""
                SELECT rest_days, recent_avg_margin, recent_win_pct
                FROM team_game_features
                WHERE game_id = 3 AND team = 'Cats'
                """)
            ).mappings().one()

        self.assertEqual(aces_game_2["rest_days"], 2)
        self.assertEqual(float(aces_game_2["recent_avg_margin"]), 10.0)
        self.assertEqual(float(aces_game_2["recent_win_pct"]), 1.0)
        self.assertEqual(cats_game_3["rest_days"], 2)
        self.assertEqual(float(cats_game_3["recent_avg_margin"]), -5.0)
        self.assertEqual(float(cats_game_3["recent_win_pct"]), 0.0)

    def test_row_count_validation_fails_when_completed_game_has_one_team_row(self):
        self._insert_games([
            {
                "id": 1,
                "external_game_id": "game-1",
                "game_date": date(2026, 1, 1),
                "home_team": "Aces",
                "away_team": "Bears",
                "home_score": 90,
                "away_score": 80,
                "spread_home": -4.5,
                "spread_away": 4.5,
            },
        ])
        self._insert_feature_row(
            game_id=1,
            team="Aces",
            opponent_team="Bears",
            is_home=True,
            team_score=90,
            opponent_score=80,
            point_diff=10,
            game_date=date(2026, 1, 1),
        )

        with self.assertRaises(TeamGameFeaturesValidationError):
            validate_completed_games_have_two_team_rows(self.database_url)

    def test_rolling_validation_fails_when_persisted_stat_is_wrong(self):
        self._insert_games([
            {
                "id": 1,
                "external_game_id": "game-1",
                "game_date": date(2026, 1, 1),
                "home_team": "Aces",
                "away_team": "Bears",
                "home_score": 90,
                "away_score": 80,
                "spread_home": -4.5,
                "spread_away": 4.5,
            },
            {
                "id": 2,
                "external_game_id": "game-2",
                "game_date": date(2026, 1, 3),
                "home_team": "Aces",
                "away_team": "Bears",
                "home_score": 82,
                "away_score": 84,
                "spread_home": -2.5,
                "spread_away": 2.5,
            },
        ])
        rows = transform_team_game_features(self.database_url)
        load_team_game_features(self.database_url, rows)

        with self.engine.begin() as connection:
            connection.execute(
                text("""
                UPDATE team_game_features
                SET recent_avg_margin = 999
                WHERE game_id = 2 AND team = 'Aces'
                """)
            )

        with self.assertRaises(TeamGameFeaturesValidationError):
            validate_rolling_stats(self.database_url)

    def _create_schema(self):
        with self.engine.begin() as connection:
            connection.execute(text("""
            CREATE TABLE games (
                id INTEGER PRIMARY KEY,
                external_game_id TEXT UNIQUE,
                game_date DATE NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_score INTEGER,
                away_score INTEGER,
                spread_home NUMERIC,
                spread_away NUMERIC
            )
            """))
            connection.execute(text("""
            CREATE TABLE team_game_features (
                id INTEGER PRIMARY KEY,
                game_id INTEGER,
                team TEXT NOT NULL,
                opponent_team TEXT NOT NULL,
                is_home BOOLEAN NOT NULL,
                team_score INTEGER,
                opponent_score INTEGER,
                point_diff INTEGER,
                rest_days INTEGER,
                recent_avg_margin NUMERIC,
                recent_win_pct NUMERIC,
                is_favorite BOOLEAN,
                spread NUMERIC,
                covered_spread BOOLEAN,
                spread_diff NUMERIC,
                game_date DATE NOT NULL,
                UNIQUE(game_id, team)
            )
            """))

    def _insert_games(self, games):
        with self.engine.begin() as connection:
            connection.execute(
                text("""
                INSERT INTO games (
                    id,
                    external_game_id,
                    game_date,
                    home_team,
                    away_team,
                    home_score,
                    away_score,
                    spread_home,
                    spread_away
                ) VALUES (
                    :id,
                    :external_game_id,
                    :game_date,
                    :home_team,
                    :away_team,
                    :home_score,
                    :away_score,
                    :spread_home,
                    :spread_away
                )
                """),
                games,
            )

    def _insert_feature_row(self, **row):
        defaults = {
            "rest_days": None,
            "recent_avg_margin": None,
            "recent_win_pct": None,
            "is_favorite": None,
            "spread": None,
            "covered_spread": None,
            "spread_diff": None,
        }
        defaults.update(row)

        with self.engine.begin() as connection:
            connection.execute(
                text("""
                INSERT INTO team_game_features (
                    game_id,
                    team,
                    opponent_team,
                    is_home,
                    team_score,
                    opponent_score,
                    point_diff,
                    rest_days,
                    recent_avg_margin,
                    recent_win_pct,
                    is_favorite,
                    spread,
                    covered_spread,
                    spread_diff,
                    game_date
                ) VALUES (
                    :game_id,
                    :team,
                    :opponent_team,
                    :is_home,
                    :team_score,
                    :opponent_score,
                    :point_diff,
                    :rest_days,
                    :recent_avg_margin,
                    :recent_win_pct,
                    :is_favorite,
                    :spread,
                    :covered_spread,
                    :spread_diff,
                    :game_date
                )
                """),
                defaults,
            )


if __name__ == "__main__":
    unittest.main()
