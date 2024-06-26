from database import ConnectionManager
import sys
from logger import Logger
import asyncio


class MigrationManager:
    def __init__(self):
        self.logger = Logger(__class__.__name__).get_logger()
        self.ConnectionManager = ConnectionManager()
        self.users = """
        CREATE TABLE IF NOT EXISTS users
        (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            currency BIGINT DEFAULT 0
        ); 
        """

        self.buildings = """
        CREATE TABLE IF NOT EXISTS buildings
        (
            id SERIAL PRIMARY KEY,
            cost BIGINT UNIQUE NOT NULL,
            income BIGINT NOT NULL
        );
        """

        self.users_buildings = """
        CREATE TABLE IF NOT EXISTS users_buildings
        (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            building_id BIGINT NOT NULL,
            count BIGINT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (building_id) REFERENCES buildings(id),
            UNIQUE (user_id,building_id)
        );
        """

        self.drop_tables_string = """
        DROP TABLE IF EXISTS users_buildings;
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS buildings;
        """
        self.tables = {
            "Users": self.users,
            "Buildings": self.buildings,
            "Users_Buildings": self.users_buildings,
        }

    @Logger.log_exception
    async def drop_tables(self):
        async with self.ConnectionManager as connection:
            await connection.execute(self.drop_tables_string)
            self.logger.debug("Dropped all tables: %s", self.tables.keys())
    @Logger.log_exception
    async def create_tables(self):
        async with self.ConnectionManager as connection:
            for table in self.tables.keys():
                await connection.execute(self.tables[table])
                self.logger.debug("Created table: %s" % table)
    @Logger.log_exception
    async def recreate_tables(self):
        await self.drop_tables()
        await self.create_tables()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python tables.py <command>")
        sys.exit(1)
    migrations = MigrationManager()
    if sys.argv[1] == "create":
        await migrations.create_tables()
    elif sys.argv[1] == "drop":
        await migrations.drop_tables()
    elif sys.argv[1] == "recreate":
        await migrations.recreate_tables()
    else:
        print("Unknown command")


if __name__ == "__main__":
    asyncio.run(main())
