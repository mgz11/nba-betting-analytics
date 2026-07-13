from config.env import ODDS_API_KEY, BASE_URL
import requests
import logging 
import time

logger = logging.getLogger(__name__)

def fetch_scores_from_api(
    sport: str = "basketball_wnba",
    days_from_values: tuple[int, ...] = (1, 2, 3),
):
    """
    Fetch scores data from The Odds API.

    Args:
        sport: Sport key (e.g. basketball_wnba)
        days_from_values: daysFrom values to request from the scores API
    Returns:
        list[dict]: JSON response from API
    """

    endpoint = f"{BASE_URL}/sports/{sport}/scores"
    scores = []

    for days_from in days_from_values:
        params = {
            "apiKey": ODDS_API_KEY,
            "daysFrom": days_from,
        }

        start = time.time()
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()

            duration = time.time() - start
            logger.info(
                "Fetched scores data",
                extra={
                    "sport": sport,
                    "days_from": days_from,
                    "duration_seconds": round(duration, 2),
                    "status_code": response.status_code,
                },
            )
            scores.extend(response.json())
        except requests.exceptions.Timeout:
            logger.exception(
                "Scores API request timed out",
                extra={"sport": sport, "days_from": days_from},
            )
        except requests.exceptions.HTTPError:
            logger.exception(
                "Scores API HTTP error: %s",
                response.text,
                extra={"sport": sport, "days_from": days_from},
            )
        except requests.exceptions.RequestException:
            logger.exception(
                "Scores API request failed",
                extra={"sport": sport, "days_from": days_from},
            )

    return scores
