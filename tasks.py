from celery import Celery
from celery import Task
import celery
from logger import Logger
from celery.result import AsyncResult
import asyncio

logger = Logger("Celery").get_logger()
app = Celery('tasks', broker='redis://redis_service:6379/0', backend='redis://redis_service:6379/0')

        




@app.task()
def simple_task(reward):
    logger.info(f"Simple task executed with reward: {reward}")
    return reward

