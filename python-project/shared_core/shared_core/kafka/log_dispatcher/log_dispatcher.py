import asyncio
from typing import Optional

from shared_core.internal_logger.internal_logger import LoggingMixin

from .protocols import RetryStrategy
from ..sender import KafkaSender

class KafkaLogDispatcher(LoggingMixin):
    def __init__(
        self, 
        sender: KafkaSender, 
        topic: str, 
        retry_strategy: RetryStrategy, 
        queue_maxsize=1000, 
        loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self._sender = sender
        self._topic = topic
        self._retry_strategy = retry_strategy
        self._queue = asyncio.Queue(maxsize=queue_maxsize)
        self._loop = loop or asyncio.get_event_loop()
        self._task = self._loop.create_task(self._background_send())

    async def log(self, msg: str):
        try:
            await self._queue.put(msg)
        except asyncio.QueueFull:
            self.logger.warning("Queue full, dropping log message")

    async def _background_send(self):
        while True:
            msg = await self._queue.get()
            attempt = 0
            while True:
                try:
                    await self._sender.send(self._topic, msg)
                    break  # Success!
                except Exception as exc:
                    attempt += 1
                    self.logger.error(f"Failed to send message: {msg}, attempt {attempt}, error: {exc}")
                    should_retry = await self._retry_strategy(attempt)
                    if not should_retry:
                        self.logger.error(f"Giving up on message after {attempt} attempts: {msg}")
                        break

    async def close(self):
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
