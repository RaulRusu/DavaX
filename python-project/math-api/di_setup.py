import asyncio
from infrastructure.config import ServiceConfig
from shared_core.di import bind
from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.kafka.sender import KafkaProducerConnectionPool, AiokafkaProducerWrapper, KafkaSender, default_serializer, pydantic_json_serializer
from shared_core.config.env_loader import get_kafka_config
from shared_core.kafka.log_dispatcher import KafkaLogDispatcher, max_attempts_strategy_factory
from shared_core.di.container import container

async def register_dependencies():
    @bind(singleton=True)
    async def get_db_client() -> OracleDBClient:
        db_client = OracleDBClient()
        db_client.create_pool()
        return db_client
        
    @bind(singleton=True)
    async def get_kafka_log_pool() -> KafkaProducerConnectionPool:
        config = get_kafka_config()
        print(f"Kafka bootstrap servers: {config.bootstrap_servers}", flush=True)
        return KafkaProducerConnectionPool(
            producer_factory=lambda: AiokafkaProducerWrapper(
                bootstrap_servers=config.bootstrap_servers, 
                request_timeout_ms=config.request_timeout_ms
            ),
            maxsize=3,
        )
    
    @bind(singleton=True)
    async def get_kafka_log_dispatcher() -> KafkaLogDispatcher:
        pool = await container.resolve(KafkaProducerConnectionPool)
        log_sender = KafkaSender(
            pool=pool,
            serializer=pydantic_json_serializer
        )
        return KafkaLogDispatcher(
            sender=log_sender,
            topic='math-api-logs',
            retry_strategy=max_attempts_strategy_factory(max_attempts=3),
            queue_maxsize=1000,
            loop=asyncio.get_event_loop()
        )

    @bind(singleton=True)
    async def get_service_config() -> ServiceConfig:
        return ServiceConfig()

async def clear_dependencies():
    if container.has_instance(KafkaLogDispatcher):
        kafka_log_dispatcher = await container.resolve(KafkaLogDispatcher)
        await kafka_log_dispatcher.close()
        
    if container.has_instance(KafkaProducerConnectionPool):
        kafka_pool = await container.resolve(KafkaProducerConnectionPool)
        await kafka_pool.close()
