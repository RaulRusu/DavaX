import asyncio
from dotenv import load_dotenv
from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.di.container import container
from shared_core.di.decorators import bind
from shared_core.kafka.sender import AiokafkaProducerWrapper
from shared_core.kafka.sender import KafkaProducerConnectionPool
from shared_core.kafka.sender import KafkaSender
from shared_core.kafka.sender import default_serializer
from shared_core.kafka.log_dispatcher.log_dispatcher import KafkaLogDispatcher
from shared_core.kafka.log_dispatcher.retry_strategies import max_attempts_strategy_factory

@bind(singleton=True)
async def create_db_client() -> OracleDBClient:
    db_client = OracleDBClient()
    db_client.create_pool()
    return db_client

@bind(singleton=True)
async def create_kafka_pool() -> KafkaProducerConnectionPool:
    return KafkaProducerConnectionPool(
        producer_factory=lambda: AiokafkaProducerWrapper(bootstrap_servers="localhost:9092", request_timeout_ms=2000),
        maxsize=3,
    )

def load_test_env():
    load_dotenv(".env.test")

async def test_db_connection():
    load_test_env()
    pool = await container.resolve(OracleDBClient)
    assert pool is not None, "Database connection pool should not be None"
    assert hasattr(pool, 'ping'), "Database connection pool should have a ping method"
    assert await pool.ping(), "Database ping should succeed"
    print("Database connection test passed.")

async def test_kafka_producer():
    kafka_pool = await container.resolve(KafkaProducerConnectionPool)
    sender = KafkaSender(
        pool=kafka_pool,
        serializer=default_serializer
    )

    log_dispatcher = KafkaLogDispatcher(
        sender=sender,
        topic='test_topic',
        retry_strategy=max_attempts_strategy_factory(max_attempts=3),
        queue_maxsize=10
    )
    
    try:
        future = await sender.send('test_message', 'test')
        assert future is not None, "Kafka send should return a result"
        print("Kafka producer test passed.")
    finally:
        await kafka_pool.close()

    try:
        await log_dispatcher.log('test_message')
        print("Kafka log dispatcher test passed.")
    finally:
        await log_dispatcher.close()

#asyncio.run(test_db_connection())
asyncio.run(test_kafka_producer())