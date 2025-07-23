import asyncio
from services.autogen import queue_generation_tasks
from utils.logger import setup_logger

logger = setup_logger("SeemeGo Setup")

async def periodic_video_generation():
    logger.info("🎬 Video generation loop started.")
    while True:
        try:
            logger.info("🔁 Starting a new video generation cycle...")
            queue_generation_tasks()
        except Exception:
            logger.exception("❌ Error during video generation:")
        await asyncio.sleep(60 * 30)

if __name__ == "__main__":
    try:
        asyncio.run(periodic_video_generation())
    except Exception:
        logger.exception("🔥 Unexpected fatal error:")
