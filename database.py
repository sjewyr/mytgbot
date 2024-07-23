from typing import Type

import asyncpg

from logger import Logger
from settings import Settings


class ConnectionManager:
    def __init__(self) -> None:
        self.pool = None
        self.logger = Logger(__class__.__name__).get_logger()  # type: ignore[name-defined]
        self.connection = asyncpg.connect()
        self.connection.close()

    async def create_database(self):
        self.connection = await asyncpg.connect(
            host=Settings.database_host,
            port=Settings.database_port,
            user=Settings.database_user,
            password=Settings.database_password,
        )
        await self.connection.execute(f"CREATE DATABASE {Settings.database_name}")
        await self.connection.close()

    async def __aenter__(self) -> asyncpg.Connection:
        try:
            self.connection = await asyncpg.connect(
                host=Settings.database_host,
                port=Settings.database_port,
                user=Settings.database_user,
                database=Settings.database_name,
                password=Settings.database_password,
            )
            return self.connection
        except Exception as e:
            self.logger.error(
                str(e)
                + f" with database {Settings.database_host}:{Settings.database_port}:{Settings.database_user}:{Settings.database_password}"
            )

    async def __aexit__(self, exc_type, exc, tb):
        if self.connection:
            await self.connection.close()

    async def fetch_objects(self, query, cls: Type, *args):
        async with self as connection:
            res = await connection.fetch(query, *args)
            return [cls(**obj) for obj in res]

    async def check_database(self):
        try:
            async with self as connection:
                return await connection.execute("SELECT 1")
        except Exception:
            return False

    @Logger.log_exception
    async def drop_db(self):
        try:
            self.connection = await asyncpg.connect(
                host=Settings.database_host,
                port=Settings.database_port,
                user=Settings.database_user,
                password=Settings.database_password,
            )
            await self.connection.execute(f"DROP DATABASE {Settings.database_name}")
            await self.connection.close()
        except Exception as e:
            self.logger.error(str(e))
