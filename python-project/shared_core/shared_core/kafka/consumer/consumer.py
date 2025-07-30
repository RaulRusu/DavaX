# shared_core/kafka/consumer.py

from typing import Optional, Protocol, Any
from shared_core.internal_logger import LoggingMixin
from aiokafka import AIOKafkaConsumer
import asyncio

class MessageProcessor(Protocol):
    async def __call__(self, message: Any) -> None: ...

class KafkaConsumer(LoggingMixin):
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

    async def start(self, max_retries: int = 5, base_delay: float = 2.0):
        """Attempts to start the Kafka consumer with retries."""
        attempt = 0
        while attempt < max_retries:
            try:
                self.consumer = AIOKafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers,
                    group_id=self.group_id,
                    value_deserializer=lambda v: v.decode('utf-8'),
                    auto_offset_reset='earliest',
                    enable_auto_commit=True
                )
                await self.consumer.start()
                self.logger.info("Kafka consumer started successfully.")
                return
            except Exception as e:
                await self.consumer.stop()
                self.consumer = None
                attempt += 1
                delay = base_delay * (2 ** (attempt - 1))
                self.logger.error(f"Failed to connect to Kafka (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    self.logger.error(f"Retrying in {delay:.1f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error("Max retries reached. Could not connect to Kafka.")
                    raise

    async def run(self):
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
            self.logger.info("Consumer is not running, nothing to stop.")