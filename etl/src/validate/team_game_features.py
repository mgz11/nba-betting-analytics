import logging
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import create_engine, text

from src.transform.transform_team_game_features import WINDOW_SIZE, days_between

logger = logging.getLogger(__name__)

ROLLING_STAT_FIELDS = ("rest_days", "recent_avg_margin", "recent_win_pct")
DECIMAL_TOLERANCE = Decimal("0.000001")


class TeamGameFeaturesValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ValidationResult:
    name: str
    checked_count: int


def validate_team_game_features(database_url):
    row_count_result = validate_completed_games_have_two_team_rows(database_url)
    rolling_stats_result = validate_rolling_stats(database_url)

    logger.info(
        "Validated team game features",
        extra={
            "row_count_games_checked": row_count_result.checked_count,
            "rolling_rows_checked": rolling_stats_result.checked_count,
        },
    )

    return [row_count_result, rolling_stats_result]


def validate_completed_games_have_two_team_rows(database_url):
    engine = create_engine(database_url)

    query = text("""
    SELECT
        games.id AS game_id,
        games.external_game_id,
        games.home_team,
        games.away_team,
        COUNT(team_game_features.id) AS feature_row_count,
        COUNT(DISTINCT team_game_features.team) AS feature_team_count,
        SUM(CASE WHEN team_game_features.team = games.home_team THEN 1 ELSE 0 END) AS home_rows,
        SUM(CASE WHEN team_game_features.team = games.away_team THEN 1 ELSE 0 END) AS away_rows
    FROM games
    LEFT JOIN team_game_features
        ON team_game_features.game_id = games.id
    WHERE games.home_score IS NOT NULL
        AND games.away_score IS NOT NULL
    GROUP BY games.id, games.external_game_id, games.home_team, games.away_team
    ORDER BY games.id
    """)

    with engine.connect() as connection:
        games = connection.execute(query).mappings().all()

    failures = []
    for game in games:
        feature_row_count = int(game["feature_row_count"] or 0)
        feature_team_count = int(game["feature_team_count"] or 0)
        home_rows = int(game["home_rows"] or 0)
        away_rows = int(game["away_rows"] or 0)

        if (
            feature_row_count != 2
            or feature_team_count != 2
            or home_rows != 1
            or away_rows != 1
        ):
            failures.append(
                (
                    game["game_id"],
                    game["external_game_id"],
                    feature_row_count,
                    feature_team_count,
                    home_rows,
                    away_rows,
                )
            )

    if failures:
        details = "; ".join(
            "game_id={game_id}, external_game_id={external_game_id}, "
            "rows={rows}, teams={teams}, home_rows={home_rows}, away_rows={away_rows}".format(
                game_id=game_id,
                external_game_id=external_game_id,
                rows=rows,
                teams=teams,
                home_rows=home_rows,
                away_rows=away_rows,
            )
            for game_id, external_game_id, rows, teams, home_rows, away_rows in failures
        )
        raise TeamGameFeaturesValidationError(
            "Each completed game must have exactly 2 team_game_features rows: "
            f"{details}"
        )

    return ValidationResult("completed_games_have_two_team_rows", len(games))


def validate_rolling_stats(database_url):
    engine = create_engine(database_url)

    games_query = text("""
    SELECT
        id,
        game_date,
        home_team,
        away_team,
        home_score,
        away_score
    FROM games
    WHERE home_score IS NOT NULL
        AND away_score IS NOT NULL
    ORDER BY game_date, id
    """)

    feature_query = text("""
    SELECT
        game_id,
        team,
        rest_days,
        recent_avg_margin,
        recent_win_pct
    FROM team_game_features
    """)

    with engine.connect() as connection:
        games = connection.execute(games_query).mappings().all()
        feature_rows = connection.execute(feature_query).mappings().all()

    features_by_game_team = {
        (row["game_id"], row["team"]): row
        for row in feature_rows
    }

    expected_rows = _expected_rolling_rows(games)
    failures = []

    for expected in expected_rows:
        feature = features_by_game_team.get((expected["game_id"], expected["team"]))
        if feature is None:
            failures.append(
                _format_missing_feature_failure(expected["game_id"], expected["team"])
            )
            continue

        for field in ROLLING_STAT_FIELDS:
            if not _values_match(feature[field], expected[field]):
                failures.append(
                    _format_field_failure(
                        expected["game_id"],
                        expected["team"],
                        field,
                        expected[field],
                        feature[field],
                    )
                )

    if failures:
        raise TeamGameFeaturesValidationError(
            "Rolling team_game_features stats do not match expected values: "
            + "; ".join(failures)
        )

    return ValidationResult("rolling_stats_match_expected_values", len(expected_rows))


def _expected_rolling_rows(games):
    expected_rows = []
    team_history = {}

    for game in games:
        home_team = game["home_team"]
        away_team = game["away_team"]
        home_score = game["home_score"]
        away_score = game["away_score"]

        home_expected = _calculate_expected_rolling_stats(
            game["game_date"],
            team_history.get(home_team, []),
        )
        away_expected = _calculate_expected_rolling_stats(
            game["game_date"],
            team_history.get(away_team, []),
        )

        expected_rows.append(
            _build_expected_row(game["id"], home_team, home_expected)
        )
        expected_rows.append(
            _build_expected_row(game["id"], away_team, away_expected)
        )

        team_history.setdefault(home_team, []).append({
            "game_date": game["game_date"],
            "point_diff": home_score - away_score,
            "win": home_score > away_score,
        })
        team_history.setdefault(away_team, []).append({
            "game_date": game["game_date"],
            "point_diff": away_score - home_score,
            "win": away_score > home_score,
        })

    return expected_rows


def _calculate_expected_rolling_stats(game_date, team_history):
    if not team_history:
        return None, None, None

    recent_games = team_history[-WINDOW_SIZE:]
    rest_days = days_between(game_date, team_history[-1]["game_date"])
    recent_avg_margin = sum(
        game["point_diff"] for game in recent_games
    ) / len(recent_games)
    recent_win_pct = sum(
        1 for game in recent_games if game["win"]
    ) / len(recent_games)

    return rest_days, recent_avg_margin, recent_win_pct


def _build_expected_row(game_id, team, rolling_stats):
    rest_days, recent_avg_margin, recent_win_pct = rolling_stats
    return {
        "game_id": game_id,
        "team": team,
        "rest_days": rest_days,
        "recent_avg_margin": recent_avg_margin,
        "recent_win_pct": recent_win_pct,
    }


def _values_match(actual, expected):
    if actual is None or expected is None:
        return actual is None and expected is None

    return abs(Decimal(str(actual)) - Decimal(str(expected))) <= DECIMAL_TOLERANCE


def _format_missing_feature_failure(game_id, team):
    return f"game_id={game_id}, team={team}, missing feature row"


def _format_field_failure(game_id, team, field, expected, actual):
    return (
        f"game_id={game_id}, team={team}, field={field}, "
        f"expected={expected}, actual={actual}"
    )
