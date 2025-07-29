from infrastructure.kafka.pool import KafkaProducerConnectionPool
from infrastructure.kafka.aiokafka_wrapper import AiokafkaProducerWrapper
from infrastructure.kafka.sender import KafkaSender, forever_retry_strategy
from infrastructure.kafka.serializer import default_serializer
import asyncio

async def main():
    pool = KafkaProducerConnectionPool(
        producer_factory=lambda: AiokafkaProducerWrapper(bootstrap_servers="localhost:9092", request_timeout_ms=2000),
        maxsize=3,
    )
    sender = KafkaSender(
        pool=pool,
        retry_strategy=forever_retry_strategy,
        serializer=default_serializer
    )
    index = 0
    while True:
        await sender.send(f"Test message {index}", topic="math-api-logs")
        index += 1
        await asyncio.sleep(3)

asyncio.run(main())