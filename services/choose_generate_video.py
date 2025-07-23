import random 
import logging
from typing import Callable, Tuple, List

from ai.Veo3AI import generate_video_with_veo3
from ai.LumaAI import generate_video_with_luma
from ai.RunwayAI import generate_runway_video
from ai.MidjourneyAI import generate_image_with_midjourney

logger = logging.getLogger(__name__)

# Категоризация генераторов с весами
VIDEO_GENERATORS: List[Tuple[str, Callable, str, float]] = [
    ("Veo 3 AI", generate_video_with_veo3, "universal", 0.5),
    ("Luma AI", generate_video_with_luma, "universal", 0.166),
    ("Runway AI", generate_runway_video, "universal", 0.167),
    ("Midjourney AI", lambda prompt, image_url, aspect_ratio: generate_image_with_midjourney(
        prompt=prompt,
        image_url=image_url,
        aspect_ratio=aspect_ratio,
        mode="mj_video"
    ), "image", 0.167)
]

def choose_video_generator(for_image: bool = False) -> Tuple[str, Callable]:
    """
    Возвращает (название, функция генерации видео) в зависимости от режима:
    - for_image=True → только image-to-video генераторы
    - for_image=False → любые (text-to-video и image-to-video)
    """
    valid_generators = [(n, f, t, w) for n, f, t, w in VIDEO_GENERATORS if callable(f)]

    if for_image:
        candidates = [(n, f, w) for n, f, t, w in valid_generators if t in {"image", "universal"}]
    else:
        candidates = [(n, f, w) for n, f, t, w in valid_generators]

    if not candidates:
        logger.error("❌ No compatible video generators found.")
        raise RuntimeError("No video generators available for the selected mode.")

    names, funcs, weights = zip(*candidates)
    idx = random.choices(range(len(names)), weights=weights, k=1)[0]
    name, func = names[idx], funcs[idx]

    logger.info(f"Available generators for {'image' if for_image else 'text'}: {list(names)}")
    logger.info(f"🎲 Selected {'image-to-video' if for_image else 'text-to-video'} generator: {name}")
    return name, func

