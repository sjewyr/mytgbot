import asyncio
from typing import Any, Callable, Coroutine, Iterable, Optional

from celery.result import AsyncResult

from celery_tasks import app
from logger import Logger


class TaskManager:
    """
    Convenience class for managing celery tasks, providing methods for applying tasks and w
    """

    def __init__(self) -> None:
        self.logger = Logger("TaskManager").get_logger()
        self.tasks: dict[
            AsyncResult, Optional[tuple[Callable, list[Any], dict[Any, Any]]]
        ] = {}
        asyncio.create_task(self.catch_results())

    def apply_with_delay(
        self,
        task: Callable,
        delay: int = 0,
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[dict[Any, Any]] = None,
        callback: Optional[Callable[[Any, Any, Any], Coroutine[Any, Any, Any]]] = None,
        args_for_callback=None,
        kwargs_for_callback=None,
    ) -> AsyncResult:
        self.logger.info(f"Applying task {task.__name__} with delay {delay} seconds")
        _task = task.apply_async(args, kwargs, countdown=delay)  # type: ignore[attr-defined]
        self.tasks.update(
            {
                _task: [callback, args_for_callback, kwargs_for_callback]
                if callback
                else None
            }
        )
        return _task

    def wait(self, task):
        if task in self.tasks:
            return task.get()
        return ValueError(
            f"{task} should be a valid task, started by this task manager"
        )

    def apply_periodic(self, task, interval, *args, **kwargs):
        self.logger.info(
            f"Applying periodic task {task.__name__} with interval {interval} seconds"
        )
        app.add_periodic_task(
            interval, sig=task.s(), args=[*args], kwargs={**kwargs}, name=task.__name__
        )

    async def catch_results(self):
        while True:
            for task in list(self.tasks):
                if task.state == "SUCCESS" or task.state == "FAILURE":
                    self.logger.info(f"Task {task} result: {task.result}, {task.state}")
                    task.forget()
                    if self.tasks[task]:
                        callback, args, kwargs = self.tasks[task]
                        if callback:
                            if not args:
                                args = []
                            if not kwargs:
                                kwargs = {}
                            await callback(*args, **kwargs)
                    self.tasks.pop(task)
            await asyncio.sleep(3)
