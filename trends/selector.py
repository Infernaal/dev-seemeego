import os
import random
from typing import Optional
from dotenv import load_dotenv
from prompt.trend_cleaner import clean_topic
from trends.google import fetch_google_trends
from trends.gnews import fetch_gnews_trends
from trends.youtube import fetch_youtube_trends
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("TrendFetcher")

def get_random_trend() -> Optional[str]:
    """
    Получает трендовую тему из нескольких источников:
    GNews, Google Trends и YouTube Trends.
    Выбирает случайную тему из доступных и очищает её.
    """
    gnews_api_key = os.getenv("GNEWS_API_KEY")
    search_api_key = os.getenv("SEARCH_API_KEY")

    sources = []

    try:
        # Получаем тренды из GNews
        if gnews_api_key:
            gnews_trends = fetch_gnews_trends(gnews_api_key)
            if gnews_trends:
                sources.append(gnews_trends)
        else:
            logger.warning("GNEWS_API_KEY is not set")

        # Получаем тренды из Google Trends
        if search_api_key:
            google_trend = fetch_google_trends(search_api_key)
            if google_trend:
                sources.append(google_trend)
        else:
            logger.warning("SEARCH_API_KEY is not set")

        # Получаем тренды из YouTube Trends
        if search_api_key:
            youtube_trend = fetch_youtube_trends(search_api_key)
            if youtube_trend:
                sources.append(youtube_trend)

    except Exception as e:
        logger.exception("Unexpected error while fetching trends:")

    if not sources:
        logger.error("Failed to fetch trends from all sources.")
        return None

    chosen = random.choice(sources)
    logger.info(f"Selected trend topic: {chosen[:200]}...")

    return clean_topic(chosen) if chosen else None
