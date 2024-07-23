from database import ConnectionManager
from logger import Logger


class UserDAO:
    def __init__(self) -> None:
        self.connection_manager = ConnectionManager()
        self.logger = Logger(__class__.__name__).get_logger()

    @Logger.log_exception
    async def prestige_up(self, telegram_id: int) -> None:
        async with self.connection_manager as conn:
            await conn.execute(
                "UPDATE users SET prestige = prestige + 1 WHERE telegram_id = $1",
                telegram_id,
            )
            prestige = await conn.fetchval(
                "SELECT prestige FROM users WHERE telegram_id = $1", telegram_id
            )
            await conn.execute(
                "UPDATE users SET currency = 1000*$2 WHERE telegram_id = $1",
                telegram_id,
                prestige,
            )
            id = await conn.fetchval(
                "SELECT id FROM users WHERE telegram_id = $1", telegram_id
            )
            await conn.execute("DELETE FROM users_buildings WHERE user_id = $1", id)
            self.logger.info(f"User {telegram_id} prestiged up")

    @Logger.log_exception
    async def register_user(self, telegram_id: int) -> None:
        async with self.connection_manager as conn:
            await conn.execute(
                "INSERT INTO users (telegram_id) VALUES ($1)", telegram_id
            )
            self.logger.info(f"User {telegram_id} registered")

    @Logger.log_exception
    async def check_user(self, telegram_id: int) -> bool:
        async with self.connection_manager as conn:
            result = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", telegram_id
            )
            if result:
                return True
            else:
                return False

    @Logger.log_exception
    async def buy_building(self, telegram_id: int, building_id: int) -> bool:
        async with self.connection_manager as conn:
            can_afford = await conn.fetchval(
                "SELECT u.currency >= (SELECT b.cost FROM buildings b WHERE b.id = $1) FROM users u WHERE u.telegram_id = $2",
                building_id,
                telegram_id,
            )
            if not can_afford:
                self.logger.info((f"User {telegram_id} cannot afford {building_id}"))
                return False

            await conn.execute(
                "UPDATE users SET currency = currency - (SELECT b.cost FROM buildings b WHERE b.id = $1) WHERE telegram_id = $2",
                building_id,
                telegram_id,
            )
            await conn.execute(
                "INSERT INTO users_buildings (user_id, building_id, count) VALUES ((SELECT id FROM users WHERE telegram_id = $1), $2, 1) ON CONFLICT (user_id, building_id) DO UPDATE SET count = users_buildings.count + 1;",
                telegram_id,
                building_id,
            )
            return True

    @Logger.log_exception
    async def currency_tick(self):
        async with self.connection_manager as conn:
            await conn.execute(
                """UPDATE users SET currency = currency +
                               (SELECT final_res FROM
                               (SELECT user_id, SUM(result) as final_res FROM
                               (SELECT ub.user_id,
                               (SELECT count FROM users_buildings WHERE user_id = ub.user_id AND building_id=ub.building_id) * (SELECT income FROM buildings b WHERE b.id = ub.building_id) * (SELECT prestige FROM users uuu WHERE uuu.id = ub.user_id) AS result
                               FROM users_buildings ub GROUP BY ub.user_id, ub.building_id) ass GROUP BY user_id) asss WHERE user_id = id) WHERE id IN (SELECT user_id FROM users_buildings)"""
            )
            self.logger.info("Currency ticked")

    @Logger.log_exception
    async def get_currency(self, telegram_id: int) -> int:
        async with self.connection_manager as conn:
            return await conn.fetchval(
                "SELECT currency FROM users WHERE telegram_id = $1", telegram_id
            )

    async def get_income(self, telegram_id: int) -> int:
        async with self.connection_manager as conn:
            return (
                await conn.fetchval(
                    """SELECT SUM(res) FROM
                                         (SELECT user_id, (ub.count*(SELECT b.income FROM buildings b WHERE b.id = ub.building_id) * (SELECT prestige FROM users WHERE id = ub.user_id)) as res
                                         FROM users_buildings ub
                                         GROUP BY ub.user_id, ub.building_id, ub.count) temp
                                         WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)""",
                    telegram_id,
                )
                or 0
            )

    @Logger.log_exception
    async def get_currency_status(self, telegram_id: int) -> int:
        currency = await self.get_currency(telegram_id)
        income = await self.get_income(telegram_id)
        return [currency, income]

    async def get_prestige(self, telegram_id: int) -> int:
        async with self.connection_manager as conn:
            return await conn.fetchval(
                "SELECT prestige FROM users WHERE telegram_id = $1", telegram_id
            )
