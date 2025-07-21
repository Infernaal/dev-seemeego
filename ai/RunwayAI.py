import os
import time
import json
from typing import Optional
import requests
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("Runway")

API_BASE = "https://api.kie.ai"
API_TOKEN = os.getenv("KIEAI_API_KEY")

if not API_TOKEN:
    raise ValueError("Missing KIEAI_API_KEY environment variable")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

REQUEST_TIMEOUT = 60          # max per-request timeout in seconds
MAX_WAIT_TIME = 600           # total timeout for generation (10 minutes)


def generate_runway_video(
    prompt: str,
    image_url: Optional[str] = None,
    duration: int = 8,
    quality: str = "720p",
    aspect_ratio: Optional[str] = None
) -> str:
    """
    Generates a video using Runway model and returns the result URL.
    """
    session = requests.Session()
    payload = {
        "prompt": prompt,
        "imageUrl": image_url or "",
        "duration": duration,
        "quality": quality,
        "aspectRatio": aspect_ratio
    }

    # Step 1 — Send generation request
    try:
        logger.info("🚀 Sending video generation request to Runway...")
        response = session.post(
            f"{API_BASE}/api/v1/runway/generate",
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
            raise Exception("No taskId returned from Runway API")

    except requests.RequestException as e:
        logger.exception(f"❌ Failed to start Runway generation: {e}")
        raise

    logger.info(f"🕒 Polling status for taskId={task_id} (timeout: {MAX_WAIT_TIME // 60} min)")
    start_time = time.time()

    # Step 2 — Poll for result
    while True:
        if time.time() - start_time > MAX_WAIT_TIME:
            raise TimeoutError("Runway video generation timed out after 10 minutes")

        time.sleep(30)

        try:
            poll_response = session.get(
                f"{API_BASE}/api/v1/runway/record-detail",
                headers=HEADERS,
                params={"taskId": task_id},
                timeout=REQUEST_TIMEOUT
            )
            poll_response.raise_for_status()
            data = poll_response.json().get("data", {})
        except requests.RequestException as e:
            logger.warning(f"⚠️ Polling error, retrying: {e}")
            continue

        state = data.get("state")
        logger.info(f"Runway generation state: {state}")

        if state == "success":
            video_url = data.get("videoInfo", {}).get("videoUrl")
            if not video_url:
                raise Exception("Generation completed but videoUrl is missing")
            logger.info(f"✅ Runway video is ready: {video_url}")
            return video_url

        elif state == "fail":
            error_msg = data.get("errorMessage") or data.get("failMsg") or "Unknown generation failure"
            raise Exception(f"Runway generation failed: {error_msg}")

        elif state in ["wait", "queueing", "generating"]:
            logger.debug("⏳ Still generating...")
            continue

        else:
            raise Exception(f"Unknown task state returned: {state}")
