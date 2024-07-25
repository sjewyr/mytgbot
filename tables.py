"""
CLI for managing the migrations

Usage:
    python tables.py [options]

    Options:
    migrate              Run all migrations and create database if needed.
    create_db            Create the  database
    drop_db              Drop the database

    Deprecated options:
    create:              Create tables
    drop:                Drop tables
    recreate:            Recreates tables
"""

import asyncio
import os
import sys

from database import ConnectionManager
from logger import Logger
from settings import Settings


class MigrationManager:
    """
    Class for managing database migrations.
    """

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
        DROP TABLE IF EXISTS migrations;
        """
        self.tables = {
            "Users": self.users,
            "Buildings": self.buildings,
            "Users_Buildings": self.users_buildings,
        }

    @Logger.log_exception
    async def drop_tables(self):
        """
        Drops all tables defined in the manager\n
        Deprecated usage. Use migrations system instead.
        """
        self.logger.debug("Deprecetaed usage")
        async with self.ConnectionManager as connection:
            await connection.execute(self.drop_tables_string)
            self.logger.debug("Dropped all tables: %s", self.tables.keys())

    @Logger.log_exception
    async def create_tables(self):
        """
        Creates all tables defined in the manager\n
        Deprecated usage. Use migrations system instead.
        """
        self.logger.debug("Deprecetaed usage")
        async with self.ConnectionManager as connection:
            for table in self.tables.keys():
                await connection.execute(self.tables[table])
                self.logger.debug("Created table: %s" % table)

    @Logger.log_exception
    async def recreate_tables(self):
        """
        Recreates all tables defined in the manager\n
        Deprecated usage. Use migrations system instead.
        """
        self.logger.debug("Deprecetaed usage")
        await self.drop_tables()
        await self.create_tables()

    @Logger.log_exception
    async def migrate(self):
        """
        Automatically finds migrations defined in the ./migrations directory and applies them \n
        For convenience (and possibly correct behavior as a migrations are sorted like strings) migrations should be named xxxx_MigrationName.sql where xxxx is the serial number of the migration\n
        Automatically creates database if it doesn't already exist
        """
        check = await self.ConnectionManager.check_database()
        if not check:
            self.logger.debug("Database is not initialized; Trying to create...")
            try:
                await self.ConnectionManager.create_database()
                self.logger.debug("Database created successfully; Continuing...")
            except Exception as e:
                self.logger.fatal(
                    "Error while creating database: %s; Shutting down..." % str(e)
                )
                return
        async with self.ConnectionManager as connection:
            await connection.execute(
                "CREATE TABLE IF NOT EXISTS migrations (id SERIAL PRIMARY KEY, filename VARCHAR(255) NOT NULL)"
            )
            migrations_dir = os.path.join(
                os.path.curdir, os.path.dirname("migrations/")
            )
            for file in sorted(os.listdir(migrations_dir)):
                if file.endswith(".sql"):
                    self.logger.debug("Found migraitions file: %s" % file)
                    if await connection.fetchrow(
                        "SELECT * FROM migrations WHERE filename = $1", file
                    ):
                        self.logger.debug("Migration already applied: %s" % file)
                        continue
                    with open(os.path.join(migrations_dir, file), "r") as migration:
                        text = migration.read()
                        if not text:
                            self.logger.debug(
                                "Migration file is empty or incorrect: %s" % file
                            )
                            continue
                        await connection.execute(text)
                        await connection.execute(
                            "INSERT INTO migrations (filename) VALUES ($1)", file
                        )
                        self.logger.debug("Migration applied: %s" % file)

    @Logger.log_exception
    async def drop_db(self):
        """
        Drops database
        """
        self.logger.debug("Dropping database: %s" % Settings.database_name)
        await self.ConnectionManager.drop_db()

    @Logger.log_exception
    async def create_db(self):
        """
        Creates database
        """
        self.logger.debug("Creating database: %s" % Settings.database_name)
        await self.ConnectionManager.create_database()


async def main():
    if len(sys.argv) < 2:
        print("""
        Usage:
        python tables.py [options]

        Options:
        migrate              Run all migrations and create database if needed.
        create_db            Create the  database
        drop_db              Drop the database

        Deprecated options:
        create:              Create tables
        drop:                Drop tables
        recreate:            Recreates tables
        """)
        sys.exit(1)
    migrations = MigrationManager()
    if sys.argv[1] == "create":
        await migrations.create_tables()
    elif sys.argv[1] == "drop":
        await migrations.drop_tables()
    elif sys.argv[1] == "recreate":
        await migrations.recreate_tables()
    elif sys.argv[1] == "migrate":
        await migrations.migrate()
    elif sys.argv[1] == "drop_db":
        await migrations.drop_db()
    elif sys.argv[1] == "create_db":
        await migrations.create_db()
    else:
        print("Unknown command")
        print("""
        Unknown command
        Usage:
        python tables.py [options]

        Options:
        migrate              Run all migrations and create database if needed.
        create_db            Create the  database
        drop_db              Drop the database

        Deprecated options:
        create:              Create tables
        drop:                Drop tables
        recreate:            Recreates tables
        """)


if __name__ == "__main__":
    asyncio.run(main())
