from database import ConnectionManager
from logger import Logger


class UserDAO:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.logger = Logger(__class__.__name__).get_logger()

    async def register_user(self, telegram_id: int) -> None:
        async with self.connection_manager as conn:
            await conn.execute(
                "INSERT INTO users (telegram_id) VALUES ($1)", telegram_id
            )
            self.logger.info(f"User {telegram_id} registered")

    async def check_user(self, telegram_id: int) -> bool:
        async with self.connection_manager as conn:
            result = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", telegram_id
            )
            if result:
                return True
            else:
                return False
