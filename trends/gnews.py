import random
import requests
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger("GNewsTrends")

def fetch_gnews_trends(api_key: str, top_n: int = 10) -> Optional[str]:
    # �������������� ������ (������������ ��� ������ � ���� �������)
    supported_countries = [
        "au", "br", "ca", "cn", "eg", "fr", "de", "gr", "hk", "in", "ie", "it",
        "jp", "nl", "no", "pk", "pe", "ph", "pt", "ro", "ru", "sg", "se", "ch",
        "tw", "ua", "gb", "us"
    ]
    
    # �������������� ���������
    supported_categories = [
        "general", "world", "nation", "business", "technology", "entertainment",
        "sports", "science", "health"
    ]

    # �������� �������� ������
    country = random.choice(supported_countries)
    category = random.choice(supported_categories)

    # ��������� URL ������� � API GNews
    url = f"https://gnews.io/api/v4/top-headlines?country={country}&category={category}&max={top_n}&apikey={api_key}"

    try:
        # ��������� GET-������
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # ������ JSON-�����
        data = response.json()
        articles = data.get("articles", [])

        if not articles:
            logger.warning(f"No articles found for country: {country}, category: {category}")
            return None

        # �������� �������� ���� ������
        article = random.choice(articles)

        # �������� title, description � content � ���� �����
        parts = [
            article.get("title", ""),
            article.get("description", ""),
            article.get("content", "")
        ]
        combined_text = " ".join(part for part in parts if part).strip()

        logger.info(f"Country: {country.upper()}, Combined trend text: {combined_text[:200]}...")

        return combined_text if combined_text else None

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while fetching GNews trends: {e}")
    except ValueError as e:
        logger.error(f"JSON decoding error: {e}")
    except Exception as e:
        logger.exception("Unexpected error while fetching GNews trends")

    return None