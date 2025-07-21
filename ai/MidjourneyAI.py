import os
import time
import json
import random
from typing import Optional, Union
import requests
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("Midjourney")

API_BASE = "https://api.kie.ai"
API_TOKEN = os.getenv("KIEAI_API_KEY")

if not API_TOKEN:
    raise ValueError("Missing KIEAI_API_KEY environment variable")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

REQUEST_TIMEOUT = 60
MAX_WAIT_TIME = 600

def generate_image_with_midjourney(
    prompt: str,
    image_url: Optional[str] = None,
    mode: Optional[str] = "mj_txt2img",
    aspect_ratio: Optional[str] = "9:16"
) -> Union[str, tuple[str, str]]:
    session = requests.Session()

    max_attempts = 3 if mode == "mj_video" else 1

    for attempt in range(max_attempts):
        stylization = random.randint(250, 750)
        weirdness = random.randint(200, 1200)

        payload = {
            "taskType": mode,
            "speed": "fast",
            "prompt": prompt,
            "fileUrl": image_url or "",
            "aspectRatio": aspect_ratio,
            "version": "7",
            "stylization": stylization,
            "weirdness": weirdness,
            "waterMark": "",
            "callBackUrl": ""
        }

        try:
            logger.info(f"🚀 Sending Midjourney request [{mode}] (stylization={stylization}, weirdness={weirdness})... (attempt {attempt+1}/{max_attempts})")
            response = session.post(
                f"{API_BASE}/api/v1/mj/generate",
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
            if time.time() - start_time > MAX_WAIT_TIME:
                raise TimeoutError(f"Midjourney generation timed out after {MAX_WAIT_TIME} seconds")

            time.sleep(30)

            try:
                poll_response = session.get(
                    f"{API_BASE}/api/v1/mj/record-info",
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
                logger.info("⏳ Midjourney task still processing...")
                continue
            elif status == 1:
                result_info = poll_data.get("resultInfoJson", {})
                urls = [entry["resultUrl"] for entry in result_info.get("resultUrls", [])]
                if not urls:
                    raise Exception("Generation finished but no result URLs returned")
                selected_url = random.choice(urls)
                if mode == "mj_video":
                    logger.info(f"🎬 Video ready: {selected_url}")
                    return selected_url
                else:
                    logger.info(f"🖼️ Image ready: {selected_url}")
                    return selected_url, aspect_ratio
            elif status in [2, 3]:
                error_msg = poll_data.get('errorMessage', 'Unknown error')
                logger.warning(f"❌ Generation failed: {error_msg}")

                if (
                    mode == "mj_video" and
                    "internal error" in error_msg.lower() and
                    attempt < max_attempts - 1
                ):
                    logger.warning("🔁 Retrying due to internal error (mj_video only)...")
                    break
                else:
                    raise Exception(f"Generation failed: {error_msg}")
            else:
                raise Exception(f"Unknown status code: {status}")

    raise Exception("Midjourney generation failed after 3 attempts")
