import os

import dotenv

dotenv.load_dotenv(dotenv_path="./.env")


def prestige_formula(x):
    return x**2 * 10000000


class Settings:
    token = os.environ.get("TELEGRAMBOT_TOKEN")
    database_user = os.environ.get("TELEGRAMBOT_DB_USER")
    database_password = os.environ.get("TELEGRAMBOT_DB_PASSWORD")
    database_host = os.environ.get("TELEGRAMBOT_DB_HOST")
    database_port = os.environ.get("TELEGRAMBOT_DB_PORT")
    database_name = os.environ.get("TELEGRAMBOT_DB_NAME")
    log_dir = os.environ.get("TELEGRAMBOT_LOG_DIR")
    currency_tick_interval = int(
        os.environ.get("TELEGRAMBOT_CURRENCY_TICK_INTERVAL") or 60
    )
    prestige_formula = prestige_formula

    broker = os.environ.get("TELEGRAMBOT_BROKER")
    backend = os.environ.get("TELEGRAMBOT_BROKER_BACKEND")
