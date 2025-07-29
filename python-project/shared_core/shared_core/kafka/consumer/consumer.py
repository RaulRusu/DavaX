# shared_core/kafka/consumer.py

from typing import Optional, Protocol, Any, Callable, Awaitable
from aiokafka import AIOKafkaConsumer
import asyncio

class MessageProcessor(Protocol):
    async def __call__(self, message: Any) -> None: ...

class KafkaConsumer:
    def __init__(
        self, 
        topic: str,
        bootstrap_servers: str,
        processor: MessageProcessor,
        group_id: str = "default-group"
    ):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.processor = processor
        self.group_id = group_id
        self.consumer: Optional[AIOKafkaConsumer] = None  

    async def run(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda v: v.decode('utf-8'),
            auto_offset_reset='earliest',
            enable_auto_commit=True
        )
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                await self.processor(msg.value)
        finally:
            await self.stop()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None
        else:
            print("Consumer is not running, nothing to stop.")