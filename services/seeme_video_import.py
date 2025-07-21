import os
import requests
from cachetools import TTLCache
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("Import Video to SeemeGo")

_ai_service_cache = TTLCache(maxsize=100, ttl=604800)

API_BASE = os.getenv("SEEMEEGO_API_BASE", "https://seemeego.ai/api")
API_TOKEN = os.getenv("SEEMEEGO_API_TOKEN", "")


def _fetch_services() -> dict[str, int]:
    url = f"{API_BASE}/services/ai"
    headers = {"Accept": "application/json"}
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return {svc["name"]: svc["id"] for svc in data}
    except requests.RequestException as e:
        logger.error(f"Failed to fetch services from SeemeeGo: {e}")
        raise


def get_ai_service_id(name: str) -> int:
    if name not in _ai_service_cache:
        logger.debug(f"Service ID for '{name}' not in cache. Fetching fresh data.")
        services = _fetch_services()
        _ai_service_cache.clear()
        for svc_name, svc_id in services.items():
            _ai_service_cache[svc_name] = svc_id
    try:
        return _ai_service_cache[name]
    except KeyError:
        available = list(_ai_service_cache.keys())
        logger.error(f"AI service '{name}' not found. Available: {available}")
        raise ValueError(f"AI service '{name}' not found. Available: {available}")


def import_video(cover: str, link: str, ai_service_id: int) -> dict:
    url = f"{API_BASE}/video/import"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    payload = {"cover": cover, "link": link, "ai_service_id": ai_service_id}
    print(payload)
    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Failed to import video '{link}' to SeemeeGo: {e}")
        raise
