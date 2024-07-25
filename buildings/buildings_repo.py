from database import ConnectionManager
from logger import Logger

from .schemas import Building


class BuildingDAO:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.logger = Logger(__class__.__name__).get_logger()  # type: ignore[name-defined]

    @Logger.log_exception
    async def list_buildings(self, telegram_id: int) -> list[Building]:
        """
        Returns list of buildings for specified user (with prestige calculation)
        """
        res = await self.connection_manager.fetch_objects(
            "SELECT id, cost, name, income*(SELECT prestige FROM users WHERE telegram_id=$1) as income FROM buildings",
            Building,
            telegram_id,
        )
        self.logger.debug(res)
        return res

    @Logger.log_exception
    async def get_building_name(self, id: int) -> str:
        """
        Returns name of the building by its ID
        """
        async with self.connection_manager as connection:
            return await connection.fetchval(
                "SELECT name FROM buildings WHERE id = $1", id
            )
