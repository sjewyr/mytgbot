from enum import Enum

from database import ConnectionManager
from logger import Logger
from tasks.schema import UserTask
from users.user_repo import UserDAO


class TaskStatus(Enum):
    OK = 0
    INSUFFICIENT_LEVEL = 1
    NOT_ENOUGH_MONEY = 2
    ALREADY_EXECUTED = 3


class UserTaskDAO:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.logger = Logger(__class__.__name__).get_logger()  # type: ignore[name-defined]

    @Logger.log_exception
    async def get_tasks(self, telegram_id) -> list[UserTask]:
        """
        Method to return all tasks with prestige calculation.
        """
        async with self.connection_manager as conn:
            prestige = await conn.fetchval(
                "SELECT prestige FROM users WHERE telegram_id = $1", telegram_id
            )
        tasks = await self.connection_manager.fetch_objects(
            "SELECT id, name, reward*$1 as reward, exp_reward*$1 as exp_reward, lvl_required, cost, length FROM user_tasks",
            UserTask,
            prestige,
        )
        return tasks

    async def task_completed(self, telegram_id, task_id) -> None:
        """
        Method to reward task completion
        """
        async with self.connection_manager as conn:
            reward, exp_reward = await conn.fetchrow(
                "SELECT reward, exp_reward FROM user_tasks WHERE id = $1", task_id
            )
            await conn.execute(
                "UPDATE users SET currency = currency + $1 WHERE telegram_id = $2",
                reward,
                telegram_id,
            )
            await conn.execute(
                "DELETE FROM user_user_tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)",
                telegram_id,
            )
            await UserDAO().get_xp(telegram_id, exp_reward)
            self.logger.info(f"Task completion {task_id} by {telegram_id}")

    async def get_task(self, telegram_id, task_id) -> UserTask:
        """
        Method to get task by id
        """
        async with self.connection_manager as conn:
            prestige = await conn.fetchval(
                "SELECT prestige FROM users WHERE telegram_id = $1", telegram_id
            )
            task = await self.connection_manager.fetch_objects(
                "SELECT id, name, reward*$1 as reward, exp_reward*$1 as exp_reward, lvl_required, cost, length FROM user_tasks WHERE id = $2",
                UserTask,
                prestige,
                task_id,
            )
            task = task[0]
            return task

    async def can_afford(self, telegram_id, task_id):
        """Method to check if user can afford a task

        :param telegram_id: telegram id of user
        :param task_id: id of the task
        """
        active_task = await self.get_active_user_task(telegram_id)
        self.logger.debug(f"for user {telegram_id}: {active_task}")
        if active_task:
            return TaskStatus.ALREADY_EXECUTED
        async with self.connection_manager as conn:
            cost = await conn.fetchval(
                "SELECT cost FROM user_tasks WHERE id = $1", task_id
            )
            currency = await conn.fetchval(
                "SELECT currency FROM users WHERE telegram_id = $1", telegram_id
            )
            if currency < cost:
                return TaskStatus.NOT_ENOUGH_MONEY
            lvl = await conn.fetchval(
                "SELECT lvl FROM users WHERE telegram_id = $1", telegram_id
            )
            lvl_required = await conn.fetchval(
                "SELECT lvl_required FROM user_tasks WHERE id = $1", task_id
            )
            if lvl < lvl_required:
                return TaskStatus.INSUFFICIENT_LEVEL
        return TaskStatus.OK

    async def get_active_user_task(self, telegram_id) -> int | None:
        """
        Method to get active user task
        """
        async with self.connection_manager as conn:
            return await conn.fetchval(
                "SELECT task_id FROM user_user_tasks WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)",
                telegram_id,
            )

    async def start_task(self, telegram_id, task_id):
        """
        Method to start user task
        """
        self.logger.info(f"Starting task for user {telegram_id}")
        async with self.connection_manager as conn:
            await conn.execute(
                "INSERT INTO user_user_tasks (user_id, task_id) VALUES ((SELECT id FROM users WHERE telegram_id = $1), $2)",
                telegram_id,
                task_id,
            )
