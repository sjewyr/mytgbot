"""
Module for logging in the application, provides Logger class which logs into the stdout and log directory defined in the configuration
"""

import datetime
import logging
import os
from functools import wraps

import colorlog

from settings import Settings

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
if not os.path.exists(log_dir):  # type: ignore[arg-type]
    os.makedirs(log_dir)  # type: ignore[arg-type]

# Хендлер для потока
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Хендлер для файла последнего запуска с режимом 'w' (write)
last_startup_file_handler = logging.FileHandler(
    os.path.join(log_dir, "last_startup.log"),  # type: ignore[arg-type]
    mode="w",  # type: ignore[arg-type]
)
last_startup_file_handler.setFormatter(file_format)

# Хендлер для файла с текущей датой с режимом 'a' (append)
date_file_handler = logging.FileHandler(
    os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log"),  # type: ignore[arg-type]
    mode="a",
)
date_file_handler.setFormatter(file_format)


class Logger:
    """
    Logger conveneince class,
    provides a single point of access to the logger,
    adds handlers for stdout and log file,
    and adds static decorator to log exceptions.\n
    Logger should be accessed via get_logger method and used as a built-in logging.
    """

    def __init__(self, name):
        """
        Initialize logger with provided name
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Добавление уже созданных хендлеров к логгеру
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(last_startup_file_handler)
        self.logger.addHandler(date_file_handler)

    def get_logger(self):
        """
        Returns logger instance
        """
        return self.logger

    @staticmethod
    def log_exception(func):
        """
        Decorator to log an exceptions\n
        Should be used as a static method only\n
        Should be used to decorate an awaitable functions only\n
        Should be used to decorate functions within a class that provide self.logger attribute\n
        """

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                res = await func(self, *args, **kwargs)
                return res
            except Exception as e:
                logger: Logger = self.logger  # type: ignore
                logger.exception(f"Exception in {func.__name__} " + str(e))
                raise e

        return wrapper
