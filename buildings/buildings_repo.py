from logger import Logger
from database import ConnectionManager
from buildings.schemas import Building

class BuildingDAO:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.logger = Logger(__class__.__name__).get_logger()
    @Logger.log_exception
    async def list_buildings(self) -> list[Building]:
        with self.connection_manager as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM buildings")
                res = await cursor.fetchall()
                self.logger.info(res)
                return res