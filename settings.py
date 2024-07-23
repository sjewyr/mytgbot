from attr import dataclass
import dotenv
import os


dotenv.load_dotenv(dotenv_path="./.env")


class Settings:
    token = os.environ.get("TELEGRAMBOT_TOKEN")
    database_user = os.environ.get("TELEGRAMBOT_DB_USER")
    database_password = os.environ.get("TELEGRAMBOT_DB_PASSWORD")
    database_host = os.environ.get("TELEGRAMBOT_DB_HOST")
    database_port = os.environ.get("TELEGRAMBOT_DB_PORT")
    database_name = os.environ.get("TELEGRAMBOT_DB_NAME")
    log_dir = os.environ.get("TELEGRAMBOT_LOG_DIR")
    currency_tick_interval = int(os.environ.get("TELEGRAMBOT_CURRENCY_TICK_INTERVAL"))
    prestige_formula = lambda prestige: prestige**2*10000000
