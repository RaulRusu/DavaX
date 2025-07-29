import os

class BaseSettings:
    @staticmethod
    def _get_required(key):
        value = os.environ.get(key)
        if value is None:
            raise RuntimeError(f"Missing required environment variable: {key}")
        return value

class DatabaseSettings(BaseSettings):
    def __init__(self):
        self.db_user = self._get_required("DB_USER")
        self.db_password = self._get_required("DB_PASSWORD")
        self.db_dsn = self._get_required("DB_DSN")
        self.pool_size = int(os.environ.get("DB_POOL_SIZE", 10))

class KafkaSettings(BaseSettings):
    def __init__(self):
        self.bootstrap_servers = self._get_required("KAFKA_BOOTSTRAP_SERVERS")
        self.request_timeout_ms = int(os.environ.get("KAFKA_REQUEST_TIMEOUT_MS", 2000))

def get_db_config():
    return DatabaseSettings()

def get_kafka_config():
    return KafkaSettings()