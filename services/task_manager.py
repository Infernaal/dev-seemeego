import threading
import queue
from typing import Callable, Any
from utils.logger import setup_logger

logger = setup_logger("TaskQueue")

# Максимальный размер очереди задач
QUEUE_MAX_SIZE = 10
_task_queue: "queue.Queue[tuple[Callable[..., Any], tuple[Any, ...]]]" = queue.Queue(maxsize=QUEUE_MAX_SIZE)

# Максимальное количество одновременно работающих потоков
MAX_WORKERS = 3

def _worker_loop(worker_id: int):
    while True:
        func, args = _task_queue.get()
        func_name = getattr(func, "__name__", str(func))
        try:
            logger.info(f"[worker-{worker_id}] Starting task: {func_name}")
            func(*args)
        except Exception as e:
            logger.error(f"[worker-{worker_id}] Error while executing {func_name}: {e}", exc_info=True)
        finally:
            _task_queue.task_done()

# Запускаем пул воркеров
for i in range(MAX_WORKERS):
    thread = threading.Thread(target=_worker_loop, args=(i,), daemon=True)
    thread.start()

def enqueue_task(func: Callable[..., Any], *args: Any) -> None:
    if not callable(func):
        logger.error(f"❌ Cannot enqueue non-callable object: {func}")
        return

    try:
        _task_queue.put_nowait((func, args))
        logger.debug(f"✅ Enqueued task: {getattr(func, '__name__', str(func))} with args: {args}")
    except queue.Full:
        logger.warning("⚠️ Task queue is full (limit: 10). Dropping task.")

def _monitor_queue_loop():
    while True:
        _task_queue.join()
        logger.info("✅ All video tasks processed. Waiting 30 minutes before next cycle...")

monitor_thread = threading.Thread(target=_monitor_queue_loop, daemon=True)
monitor_thread.start()
