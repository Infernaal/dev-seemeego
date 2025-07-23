import os
import time
import json
from typing import Optional
from dotenv import load_dotenv
import requests
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("Veo3")

API_BASE = "https://api.kie.ai"
API_TOKEN = os.getenv("KIEAI_API_KEY")

if not API_TOKEN:
    raise ValueError("Missing KIEAI_API_KEY environment variable")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

REQUEST_TIMEOUT = 60         # максимум 60 секунд на один запрос
MAX_WAIT_TIME = 600          # максимум 10 минут общее ожидание генерации


def generate_video_with_veo3(
    prompt: str,
    image_url: Optional[str] = None,
    aspect_ratio: Optional[str] = None
) -> str:
    session = requests.Session()

    payload = {
        "prompt": prompt,
        "enableTranslation": True,
        "imageUrls": [image_url] if image_url else [],
        "model": "veo3_fast",
        "aspectRatio": aspect_ratio
    }

    try:
        logger.info("🚀 Sending video generation request...")
        response = session.post(
            f"{API_BASE}/api/v1/veo/generate",
            headers=HEADERS,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        response_data = response.json()

        if response_data.get("code") != 200:
            raise Exception(f"API error {response_data.get('code')}: {response_data.get('msg', 'Unknown error')}")

        task_id = response_data.get("data", {}).get("taskId")
        if not task_id:
            raise Exception("Missing 'taskId' in response")

    except requests.RequestException as e:
        logger.exception(f"❌ Request failed during generation start: {e}")
        raise

    logger.info(f"🕒 Polling taskId={task_id} (max wait: {MAX_WAIT_TIME // 60} min)...")
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_TIME:
            raise TimeoutError(f"Video generation timed out after {MAX_WAIT_TIME} seconds")

        time.sleep(30)

        try:
            poll_response = session.get(
                f"{API_BASE}/api/v1/veo/record-info",
                params={"taskId": task_id},
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            poll_response.raise_for_status()
            poll_data = poll_response.json().get("data", {})
        except requests.RequestException as e:
            logger.warning(f"⚠️ Polling failed, retrying: {e}")
            continue

        status = poll_data.get("successFlag")
        if status == 0:
            logger.info("⏳ Video generation in progress...")
            continue
        elif status == 1:
            urls = poll_data.get("response", {}).get("resultUrls", [])
            if not urls:
                raise Exception("Generation finished but no video URL returned")
            logger.info(f"✅ Video ready: {urls[0]}")
            return urls[0]
        elif status in [2, 3]:
            raise Exception(f"Video generation failed: {poll_data.get('errorMessage', 'Unknown error')}")
        else:
            raise Exception(f"Unknown status code: {status}")

