import os
import json
import time
import random
import requests
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("Kling")

API_URL = "https://api.piapi.ai"
API_KEY = os.getenv("PIAPI_API_KEY")
HEADERS = {
    'x-api-key': API_KEY,
    'Content-Type': 'application/json'
}

MAX_WAIT_TIME = 600  # 10 minutes
POLL_INTERVAL = 30

def generate_video_with_kling(prompt: str) -> str:
    cfg_scale = round(random.uniform(0, 1), 2)
    duration = 10
    aspect_ratio = "9:16"
    mode = random.choices(["pro", "std"], weights=[0.9, 0.1])[0]
    std_versions = ["1.5", "1.6"]
    pro_versions = std_versions + ["2.0"]

    version = "2.0" if mode == "pro" and random.random() < 0.90 else random.choice(std_versions)

    payload = {
        "model": "kling",
        "task_type": "video_generation",
        "input": {
            "prompt": prompt,
            "negative_prompt": "",
            "cfg_scale": cfg_scale,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "mode": mode,
            "version": version,
            "camera_control": {
                "type": "simple",
                "config": {
                    "horizontal": 0,
                    "vertical": 0,
                    "pan": -10,
                    "tilt": 0,
                    "roll": 0,
                    "zoom": 0
                }
            }
        },
        "config": {
            "service_mode": "",
            "webhook_config": {
                "endpoint": "",
                "secret": ""
            }
        }
    }

    try:
        response = requests.post(f"{API_URL}/api/v1/task", headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        task_id = data.get("data", {}).get("task_id")

        if not task_id:
            raise Exception(f"task_id missing from response: {data}")

        logger.info(f"Task created: {task_id}, polling for completion...")

        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            if elapsed > MAX_WAIT_TIME:
                raise TimeoutError("Video generation timed out after 10 minutes.")

            time.sleep(POLL_INTERVAL)
            status_resp = requests.get(f"{API_URL}/api/v1/task/{task_id}", headers=HEADERS, timeout=60)
            status_resp.raise_for_status()
            task_data = status_resp.json()
            status = task_data.get("data", {}).get("status")

            if status == "completed":
                video_url = task_data.get("data", {}).get("output", {}).get("video_url")
                if not video_url:
                    raise Exception("Task completed but no video_url returned.")
                logger.info(f"Video successfully generated: {video_url}")
                return video_url

            elif status == "failed":
                raise Exception("Video generation failed according to API status.")

            logger.info(f"Current status: {status}. Waiting...")

    except requests.RequestException as e:
        logger.error(f"HTTP request failed: {e}")
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during Kling video generation: {e}")
        raise
