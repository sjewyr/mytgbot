import asyncio

from celery import Celery

from logger import Logger
from settings import Settings
from tasks.tasks_repo import UserTaskDAO

logger = Logger("Celery").get_logger()
conf = {
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "enable_utc": True,
    "task_default_queue": "default",
    "task_default_exchange_type": "direct",
    "task_default_routing_key": "default",
    "worker_prefetch_multiplier": 1,
    "broker_heartbeat": 10,
    "broker_connection_timeout": 30,
    "task_acks_late": True,
    "task_reject_on_worker_lost": True,
    "worker_send_task_events": True,
    "task_send_sent_event": True,
    "task_track_started": True,
}
app = Celery(
    "tasks", broker=Settings.broker, backend=Settings.backend, config_source=conf
)


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


@app.task()
def start_user_task(telegram_id, task_id):
    """
    Start task for the user with given telegram_id and task_id.

    Args:
        telegram_id (int): Telegram id of the user
        task_id (int): Id of the task to be started
    """
    logger.info(f"Starting task {task_id} for user {telegram_id}")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(UserTaskDAO().task_completed(telegram_id, task_id))
