import http.client
import json
import time
import random
from utils.logger import setup_logger
from dotenv import load_dotenv
import os

load_dotenv()
logger = setup_logger("HailuoAI")


API_KEY = os.getenv("PIAPI_API_KEY")

def generate_video_with_hailuo(prompt: str) -> str:
    """
    Генерирует видео через API Hailuo.

    Args:
        prompt (str): Текстовый промпт для генерации видео.

    Returns:
        str: URL сгенерированного видео.

    Raises:
        Exception: При ошибках работы с API или отсутствии необходимых данных.
    """

    model_type = "t2v-01-director"
    expand_prompt = random.choice([True, False])  # Рандомизация расширения промпта

    payload = json.dumps({
        "model": "hailuo",
        "task_type": "video_generation",
        "input": {
            "prompt": prompt,
            "model": model_type,
            "expand_prompt": expand_prompt
        },
        "config": {
            "service_mode": "public",
            "webhook_config": {
                "endpoint": "",
                "secret": ""
            }
        }
    })

    headers = {
        'x-api-key': API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        # --- Отправка POST-запроса на создание задачи ---
        conn = http.client.HTTPSConnection("api.piapi.ai", timeout=10)
        conn.request("POST", "/api/v1/task", payload, headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")
        data = json.loads(raw_data)
        conn.close()

        logger.info(f"Task creation response: {data}")

        task_id = data.get("data", {}).get("task_id")
        if not task_id:
            raise Exception("Failed to obtain task_id from response")

        # --- Опрос статуса задачи с интервалом 30 секунд ---
        while True:
            time.sleep(30)
            conn = http.client.HTTPSConnection("api.piapi.ai", timeout=10)
            conn.request("GET", f"/api/v1/task/{task_id}", headers=headers)
            res = conn.getresponse()
            raw_status = res.read().decode("utf-8")
            status_data = json.loads(raw_status)
            conn.close()

            status = status_data.get("data", {}).get("status")
            logger.info(f"Task status: {status}")

            if status == "completed":
                video_url = status_data.get("data", {}).get("output", {}).get("download_url")
                if not video_url:
                    raise Exception("Task completed but download_url is missing")
                logger.info(f"Video generation completed successfully, URL: {video_url}")
                return video_url

            elif status == "failed":
                raise Exception("Task failed during video generation")

            # Можно логировать остальные статусы, например: pending, running, etc.
            else:
                logger.info(f"Waiting for task completion, current status: {status}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        raise

    except http.client.HTTPException as e:
        logger.error(f"HTTP error during request: {e}")
        raise

    except Exception as e:
        logger.exception(f"Unexpected error during video generation: {e}")
        raise
