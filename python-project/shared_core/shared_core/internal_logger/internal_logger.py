from logging import getLogger, INFO, StreamHandler, Formatter

class BaseInternalLogger:
    LOGGER_NAME = "internal_logger"

    def __init__(self):
        self._logger = getLogger(self.LOGGER_NAME)
        self._logger.setLevel(INFO)

        if not self._logger.hasHandlers():
            handler = StreamHandler()
            handler.setFormatter(Formatter('%(levelname)s internal: %(message)s'))
            self._logger.addHandler(handler)

    def log(self, level: int, message: str):
        self._logger.log(level, message)

    def error(self, message: str):
        self._logger.error(message)

    def info(self, message: str):
        self._logger.info(message)

    def debug(self, message: str):
        self._logger.debug(message)
    
    def warning(self, message: str):
        self._logger.warning(message)



from shared_core.di.container import container, DependencyNotFound
from threading import Lock

class LoggingMixin:
    _logger_instance = None
    _logger_lock = Lock()

    @property
    def logger(self) -> BaseInternalLogger:
        if self._logger_instance is not None:
            return self._logger_instance

        with self._logger_lock:
            # Double-checked locking pattern
            if self._logger_instance is not None:
                return self._logger_instance
            try:
                self._logger_instance = container.resolve_sync(BaseInternalLogger)
            except DependencyNotFound:
                self._logger_instance = BaseInternalLogger()
                self._logger_instance.info("BaseInternalLogger not found in DI container, using default instance.")
        return self._logger_instance