import os
import time
import requests
import random
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import lumaai
from lumaai import LumaAI
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger("LumaAI")

API_TOKEN = os.getenv("LUMAAI_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not API_TOKEN:
    raise ValueError("Missing LUMAAI_API_KEY environment variable")
if not OPENAI_KEY:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

client = LumaAI(auth_token=API_TOKEN)
openai_client = OpenAI(api_key=OPENAI_KEY)

VIDEO_TIMEOUT = 600   # 10 minutes
AUDIO_TIMEOUT = 300   # 5 minutes


def generate_audio_prompt(video_prompt: str) -> str:
    system_prompt = (
        "You are a professional sound designer for viral short videos. "
        "Given a video prompt, generate a short, vivid audio prompt description. "
        "Mention energy level (calm, energetic, etc.), tone, atmosphere, instruments, and genre. "
        "Use under 20 words. Do not reference brands, artists, or songs. No quotes or extra text."
    )

    user_prompt = f"Generate an audio prompt for this video: {video_prompt}"

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    audio_description = response.choices[0].message.content.strip()
    logger.info(f"[audio_prompt] Generated audio prompt: {audio_description}")
    return audio_description


def generate_video_with_luma(
    prompt: str,
    image_url: Optional[str] = None,
    aspect_ratio: Optional[str] = None
) -> str:
    try:
        model = "ray-flash-2"
        resolution = "1080p"

        logger.info("🚀 Sending video generation request to Luma...")
        try:
            generation = client.generations.create(
                model=model,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                duration="9s",
                loop=False,
                prompt=prompt,
            )
        except lumaai.APIConnectionError as e:
            logger.error("LumaAI: Could not reach the server", exc_info=True)
            raise
        except lumaai.RateLimitError as e:
            logger.error("LumaAI: Rate limit exceeded", exc_info=True)
            raise
        except lumaai.APIStatusError as e:
            logger.error(f"LumaAI: Non-200 status code: {e.status_code}", exc_info=True)
            raise

        logger.info(f"Polling video generation (ID: {generation.id})...")
        start_time = time.time()

        while True:
            if time.time() - start_time > VIDEO_TIMEOUT:
                raise TimeoutError("LumaAI video generation timed out after 10 minutes")

            time.sleep(30)
            generation = client.generations.get(id=generation.id)

            if generation.state == "completed":
                video_url = generation.assets.video
                if not video_url:
                    raise Exception("Video generation completed, but no video URL returned")
                logger.info(f"✅ Video generated: {video_url}")
                break

            elif generation.state == "failed":
                reason = generation.failure_reason or "Unknown error"
                raise Exception(f"LumaAI video generation failed: {reason}")

            logger.info(f"Video status: {generation.state}... Waiting...")

        # Add audio
        audio_prompt = generate_audio_prompt(prompt)
        if audio_prompt:
            logger.info("🎵 Adding audio to video...")
            audio_url = f"https://api.lumalabs.ai/dream-machine/v1/generations/{generation.id}/audio"

            headers = {
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            json_data = {
                "generation_type": "add_audio",
                "prompt": audio_prompt
            }

            try:
                response = requests.post(audio_url, headers=headers, json=json_data)
                response.raise_for_status()
                audio_generation = response.json()
                audio_generation_id = audio_generation["id"]
            except requests.RequestException as e:
                logger.error("Failed to start audio generation", exc_info=True)
                raise

            logger.info(f"Polling audio generation (ID: {audio_generation_id})...")
            audio_start_time = time.time()

            while True:
                if time.time() - audio_start_time > AUDIO_TIMEOUT:
                    raise TimeoutError("LumaAI audio generation timed out after 5 minutes")

                time.sleep(30)
                try:
                    status_resp = requests.get(
                        f"https://api.lumalabs.ai/dream-machine/v1/generations/{audio_generation_id}",
                        headers=headers
                    )
                    status_resp.raise_for_status()
                    status_data = status_resp.json()
                except requests.RequestException as e:
                    logger.warning("Polling audio generation failed, retrying...", exc_info=True)
                    continue

                state = status_data.get("state")
                if state == "completed":
                    video_with_audio_url = status_data["assets"]["video"]
                    logger.info(f"✅ Video with audio is ready: {video_with_audio_url}")
                    return video_with_audio_url
                elif state == "failed":
                    reason = status_data.get("failure_reason", "Unknown error")
                    raise Exception(f"Audio generation failed: {reason}")
                else:
                    logger.info(f"Audio status: {state}... Waiting...")

        return video_url

    except Exception as e:
        logger.exception(f"❌ Error during LumaAI generation: {e}")
        raise
