from asyncio import Future
from typing import Optional
from aiokafka import AIOKafkaProducer
from aiokafka.structs import RecordMetadata

class AiokafkaProducerWrapper:
    def __init__(self, bootstrap_servers: str, **kwargs):
        self._producer: Optional[AIOKafkaProducer] = None
        self._bootstrap_servers = bootstrap_servers
        self._kwargs = kwargs

    async def start(self):
        self._producer = AIOKafkaProducer(bootstrap_servers=self._bootstrap_servers, **self._kwargs)
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()
            self._producer = None

    async def send(self, topic: str, value: bytes) -> Future[RecordMetadata]:
        if not self._producer:
            raise RuntimeError("Producer is not started")
        return await self._producer.send(topic, value=value)
