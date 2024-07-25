from celery import Celery

from logger import Logger
from settings import Settings

logger = Logger("Celery").get_logger()
app = Celery("tasks", broker=Settings.broker, backend=Settings.backend)


@app.task()
def simple_task(reward):
    logger.info(f"Simple task executed with reward: {reward}")
    return reward


@app.task()
def await_check_init():
    """
    Check if task system is initialized correctly.

    Returns:
        bool: True if initialized correctly
    """
    logger.info("Checking task system initialization...")
    return True
