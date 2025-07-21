import random
import requests
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger("YouTubeTrends")

def fetch_youtube_trends(api_key: str, category: str = "now", top_n: int = 10) -> Optional[str]:
    """
    Получает тренды YouTube с помощью SearchAPI.io.
    Выбирает случайное видео из топ-N трендов.
    """
    # Поддерживаемые страны для параметра gl
    supported_countries = [
        "US", "IN", "KR", "JP", "BR", "MX",
        "GB", "RU", "FR", "DE", "ID", "PH"
    ]

    # Сопоставление страны с языком (hl)
    default_languages = {
        "US": "en", "GB": "en", "IN": "en", "KR": "ko", "JP": "ja",
        "BR": "pt", "MX": "es", "RU": "ru", "FR": "fr", "DE": "de",
        "ID": "id", "PH": "en"
    }

    # Случайно выбираем страну и язык
    gl = random.choice(supported_countries)
    hl = default_languages.get(gl, "en")

    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "youtube_trends",
        "bp": category,
        "gl": gl,
        "hl": hl,
        "api_key": api_key
    }

    try:
        # Отправляем запрос к API
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        trending = data.get("trending", [])

        if not trending:
            logger.warning(f"No trending videos found for gl={gl}, hl={hl}, category={category}")
            return None

        # Выбираем случайное видео из топ-N
        top_trending = trending[:top_n]
        video = random.choice(top_trending)

        title = video.get("title")
        logger.info(f"Country: {gl}, Language: {hl}, Category: {category}, Video title: {title}")

        return title if title else None

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while fetching YouTube trends: {e}")
    except ValueError as e:
        logger.error(f"JSON decoding error: {e}")
    except Exception as e:
        logger.exception("Unexpected error while fetching YouTube trends")

    return None
