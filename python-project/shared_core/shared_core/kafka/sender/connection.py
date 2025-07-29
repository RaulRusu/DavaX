from asyncio import Lock, Future
from collections.abc import Callable
from .protocols import AsyncKafkaProducer
from aiokafka.structs import RecordMetadata
from aiokafka.errors import KafkaConnectionError

class KafkaProducerConnection:
    """
    Wraps a single async Kafka producer connection.
    Connects lazily: only on first send() or explicit connect().
    """
    def __init__(self, producer_factory: Callable[[], AsyncKafkaProducer]):
        self._producer: AsyncKafkaProducer = producer_factory()
        self._connected = False
        self._lock = Lock()

    async def connect(self):
        async with self._lock:
            if not self._connected:
                try:
                    await self._producer.start()
                except KafkaConnectionError as e:
                    await self._producer.stop()
                    raise
                self._connected = True

    async def send(self, topic: str, data: bytes) ->Future[RecordMetadata]:
        await self.connect()  # Ensure connection before sending
        return await self._producer.send(topic, data)

    async def close(self):
        async with self._lock:
            if self._connected:
                await self._producer.stop()
                self._connected = False

    @property
    def is_connected(self):
        return self._connected
