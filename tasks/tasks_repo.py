from database import ConnectionManager
from logger import Logger
from tasks.schema import UserTask


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
