from services.log_service import LogService, LogProcessor
from shared_core.di import bind
from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.kafka.consumer import KafkaConsumer
from shared_core.config.env_loader import get_kafka_config
from shared_core.di.container import container
from stores.log_store import ServiceLogStore
from shared_core.internal_logger import BaseInternalLogger

async def register_dependencies():
    @bind(singleton=True)
    async def get_db_client() -> OracleDBClient:
        db_client = OracleDBClient()
        db_client.create_pool()
        return db_client
    
    @bind(singleton=True)
    async def get_log_store() -> ServiceLogStore:
        db_client = await container.resolve(OracleDBClient)
        return ServiceLogStore(db_client)
    
    @bind(singleton=True)
    async def get_log_service() -> LogService:
        log_store = await container.resolve(ServiceLogStore)
        return LogService(log_store)
    
    @bind(singleton=True)
    async def get_kafka_log_consumer() -> KafkaConsumer:
        config = get_kafka_config()

        log_service = await container.resolve(LogService)
        log_processor = LogProcessor(log_service)

        return KafkaConsumer(
            topic='math-api-logs',
            bootstrap_servers=config.bootstrap_servers,
            processor=log_processor,
            group_id='log_processor'
        )
    
    @bind(singleton=True)
    def get_internal_logger() -> BaseInternalLogger:
        return BaseInternalLogger()