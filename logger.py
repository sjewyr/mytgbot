import logging
import colorlog
import datetime
import os
from settings import Settings
from functools import wraps


# Создание цветного форматера
log_colors = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

formatter = colorlog.ColoredFormatter(
    "%(log_color)s [%(levelname)s %(asctime)s]: (%(name)s) %(message)s",
    log_colors=log_colors,
)
file_format = logging.Formatter("[%(levelname)s %(asctime)s]: (%(name)s) %(message)s")


# Создаем хендлеры, которые будут использоваться всеми логгерами
log_dir = Settings.log_dir
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Хендлер для потока
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Хендлер для файла последнего запуска с режимом 'w' (write)
last_startup_file_handler = logging.FileHandler(
    os.path.join(log_dir, "last_startup.log"), mode="w"
)
last_startup_file_handler.setFormatter(file_format)

# Хендлер для файла с текущей датой с режимом 'a' (append)
date_file_handler = logging.FileHandler(
    os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log"),
    mode="a",
)
date_file_handler.setFormatter(file_format)


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Добавление уже созданных хендлеров к логгеру
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(last_startup_file_handler)
        self.logger.addHandler(date_file_handler)

    def get_logger(self):
        return self.logger

    @staticmethod
    def log_exception(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                res = await func(self, *args, **kwargs)
                return res
            except Exception as e:
                logger: Logger = self.logger
                logger.exception(f"Exception in {func.__name__} " + str(e))
                raise e

        return wrapper
