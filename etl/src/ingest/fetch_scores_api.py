from config.env import ODDS_API_KEY, BASE_URL
import requests
import logging 
import time

logger = logging.getLogger(__name__)

def fetch_scores_from_api(sport: str = "basketball_wnba"):
    """
    Fetch scores data from The Odds API.

    Args:
        sport: Sport key (e.g. basketball_wnba)
    Returns:
        list[dict]: JSON response from API
    """

    endpoint = f"{BASE_URL}/sports/{sport}/scores"
    params = {
        "apiKey": ODDS_API_KEY,
        "daysFrom": 2
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
                "duration_seconds": round(duration, 2),
                "status_code": response.status_code,
            },
        )
        return response.json()
    except requests.exceptions.Timeout:
        logger.exception("Scores API request timed out")
        return []
    except requests.exceptions.HTTPError:
        logger.exception("Scores API HTTP error: %s", response.text)
        return []
    except requests.exceptions.RequestException:
        logger.exception("Scores API request failed")
        return []