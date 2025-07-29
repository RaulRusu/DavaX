from typing import Any
from .pool import KafkaProducerConnectionPool
from .protocols import MessageSerializer
from aiokafka.structs import RecordMetadata

class KafkaSender:
    def __init__(
        self,
        pool: KafkaProducerConnectionPool,
        serializer: MessageSerializer
    ) -> None:
        self._pool = pool
        self._serializer = serializer

    async def send(self, topic: str, msg: Any) -> RecordMetadata:
        async with self._pool.connection() as conn:
            data = self._serializer(msg)
            future = await conn.send(topic, data)
            return await future
