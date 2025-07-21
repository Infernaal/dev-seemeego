import random
import requests
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger("GoogleTrends")

def fetch_google_trends(api_key: str, time_range: str = "past_4_hours", top_n: int = 10) -> Optional[str]:
    """
    Получает тренды Google по заданному региону и временному диапазону.
    Выбирает случайный тренд из топ-N.
    """
    # Список поддерживаемых стран с краткими комментариями
    supported_countries = [
        "US",  # США – глобальные тренды, TikTok, выборы, шоу-бизнес
        "KR",  # Южная Корея – K-pop, дорамы, стиль, тренды
        "JP",  # Япония – аниме, инновации, катастрофы
        "GB",  # Великобритания – королевская семья, футбол, политика
        "IN",  # Индия – Болливуд, фестивали, политические события
        "BR",  # Бразилия – футбол, карнавалы, протесты
        "UA",  # Украина – война, героизм, волонтерство, глобальный резонанс
        "RU",  # Россия – пропаганда, конфликты, YouTube-мемы
        "FR",  # Франция – мода, протесты, культура
        "DE",  # Германия – ЕС, экономика, технологии
        "MX",  # Мексика – политика, криминал, яркие события
        "IT"   # Италия – стиль жизни, мода, скандалы, культура
    ]

    # Случайно выбираем регион
    geo = random.choice(supported_countries)

    url = "https://www.searchapi.io/api/v1/search"
    params = {
        "engine": "google_trends_trending_now",
        "geo": geo,
        "time": time_range,
        "api_key": api_key
    }

    try:
        # Запрос к API с таймаутом для защиты от зависаний
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        trends = data.get("trends", [])

        if not trends:
            logger.warning(f"No trends found for geo: {geo}")
            return None

        # Выбираем случайный тренд из топ-N
        top_trends = trends[:top_n]
        trend = random.choice(top_trends)

        query = trend.get("query")
        logger.info(f"Geo: {geo}, Trend: {query}")

        return query if query else None

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while fetching Google trends: {e}")
    except ValueError as e:
        logger.error(f"JSON decoding error: {e}")
    except Exception as e:
        logger.exception("Unexpected error while fetching Google trends")

    return None
