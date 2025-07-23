from prompt.text_to_video_prompt import generate_prompt 

from generators.text_to_video import generate_text_to_video
from services.choose_generate_video import choose_video_generator
from services.task_manager import enqueue_task
from services.convert_cover_image import extract_frame_from_video, generate_image_url
from services.seeme_video_import import get_ai_service_id, import_video
from trends.selector import get_random_trend
from prompt.category_prompt import get_custom_topic_from_category
import random
import logging
from prompt.text_image_video_prompt import (
    generate_image_prompt,
    generate_portrait_prompt,
    generate_prompt as generate_scene_prompt
)
from ai.MidjourneyAI import generate_image_with_midjourney

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 1

def enqueue_with_retry(task_func, current_try=0):
    if current_try < MAX_RETRIES:
        enqueue_task(lambda: task_func(current_try + 1))
    else:
        logger.warning(f"🚫 Too many retries for task {task_func.__name__}. Dropping after {MAX_RETRIES} attempts.")

def process_text_to_video_generation(current_try=0):
    try:
        description = generate_text_to_video()
        name, generator_func = choose_video_generator(for_image=False)
        aspect_ratio = "9:16"
        video_url = generator_func(description, aspect_ratio=aspect_ratio)

        if not video_url:
            logger.warning("No video URL returned (text-to-video), re-enqueueing...")
            enqueue_with_retry(process_text_to_video_generation, current_try)
            return
        
        logger.info(f"[text-to-video] ✅ Prompt: {description}, engine={name}, 🎬 URL: {video_url}")
        
        image_path = extract_frame_from_video(video_url, at_second=1.0)
        image_url = generate_image_url(image_path)
        try:
            ai_id = get_ai_service_id(name)
            response = import_video(image_url, video_url, ai_id)
            logger.info(f"Imported video to server: {response}")
        except Exception as e:
            logger.exception(f"❌ Error importing video: {e}")

    except Exception as e:
        logger.exception(f"❌ Error in text-to-video generation: {e}")
        enqueue_with_retry(process_text_to_video_generation, current_try)

def _run_image_to_video(prompt_func, retry_func, current_try=0):
    try:
        prompt = prompt_func()
        image_url, aspect_ratio = generate_image_with_midjourney(prompt, mode="mj_txt2img") 
        description = generate_scene_prompt(image_url, prompt)
        name, generator_func = choose_video_generator(for_image=True)
        video_url = generator_func(description, image_url, aspect_ratio=aspect_ratio)

        if not video_url:
            logger.warning("No video URL returned (image-to-video), re-enqueueing...")
            enqueue_with_retry(lambda t=current_try: retry_func(t), current_try)
            return
        
        tag = "portrait-to-video" if prompt_func is generate_portrait_prompt else "image-to-video"
        logger.info(f"[{tag}] ✅ Prompt: {description}, engine={name}, 🎬 URL: {video_url}")

        try:
            ai_id = get_ai_service_id(name)
            response = import_video(image_url, video_url, ai_id)
            logger.info(f"Imported video to server: {response}")
        except Exception as e:
            logger.exception(f"❌ Error importing video: {e}")

    except Exception as e:
        logger.exception(f"❌ Error in image-to-video generation ({prompt_func.__name__}): {e}")
        enqueue_with_retry(lambda t=current_try: retry_func(t), current_try)

def process_portrait_image_to_video_generation(current_try=0):
    _run_image_to_video(generate_portrait_prompt, process_portrait_image_to_video_generation, current_try)

def process_image_prompt_to_video_generation(current_try=0):
    _run_image_to_video(generate_image_prompt, process_image_prompt_to_video_generation, current_try)

def queue_generation_tasks():
    """
    Кладёт в очередь задачи на генерацию видео
    (в будущем — может быть кастомные категории, тренды и т.п.)
    """

    # Отключаем генерацию трендов и категорий
    # try:
    #     trend_topic = get_random_trend()
    # except Exception as e:
    #     logger.error(f"Failed to get random trend topic: {e}")
    #     trend_topic = None

    # try:
    #     custom_topic = get_custom_topic_from_category()
    # except Exception as e:
    #     logger.error(f"Failed to get custom category topic: {e}")
    #     custom_topic = None

    # if trend_topic:
    #     enqueue_task(process_generation, trend_topic)
    #     logger.info(f"Enqueued task with trend topic: '{trend_topic}'")
    # else:
    #     logger.warning("No trend topic obtained, skipping enqueue for trend task.")

    # if custom_topic:
    #     enqueue_task(process_generation, custom_topic)
    #     logger.info(f"Enqueued task with custom topic: '{custom_topic}'")
    # else:
    #     logger.warning("No custom topic obtained, skipping enqueue for custom task.")

    enqueue_task(process_text_to_video_generation)
    enqueue_task(process_portrait_image_to_video_generation)
    enqueue_task(process_image_prompt_to_video_generation)
    logger.info("Enqueued tasks: text-to-video, portrait-image-to-video, image-to-video.")
