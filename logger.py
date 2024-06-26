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


class Logger(logging.Logger):
    def __init__(self, name):
        super().__init__(name)
        self.setLevel(logging.DEBUG)

        # Добавление уже созданных хендлеров к логгеру
        self.addHandler(stream_handler)
        self.addHandler(last_startup_file_handler)
        self.addHandler(date_file_handler)

    def get_logger(self):
        return self

    @staticmethod
    def log_exception(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                logger: Logger = self.logger
                logger.exception(f"Exception in {func.__name__} " + str(e))
                raise e
        return wrapper
            
