import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Set
from .connection import KafkaProducerConnection

class KafkaProducerConnectionPool:
    """
    Async connection pool for Kafka producer connections, lazily connects.
    """
    def __init__(self, producer_factory: Callable[[], KafkaProducerConnection], maxsize: int = 5) -> None:
        self._producer_factory: Callable[[], KafkaProducerConnection] = producer_factory
        self._maxsize: int = maxsize
        self._pool: asyncio.LifoQueue[KafkaProducerConnection] = asyncio.LifoQueue(maxsize)
        self._used: Set[KafkaProducerConnection] = set()
        self._lock: asyncio.Lock = asyncio.Lock()
        for _ in range(self._maxsize):
            self._pool.put_nowait(KafkaProducerConnection(self._producer_factory))

    async def acquire(self) -> KafkaProducerConnection:
        conn = await self._pool.get()
        async with self._lock:
            self._used.add(conn)
        return conn

    async def release(self, conn: KafkaProducerConnection) -> None:
        async with self._lock:
            if conn in self._used:
                self._used.discard(conn)
        await self._pool.put(conn)

    async def close(self) -> None:
        async with self._lock:
            while not self._pool.empty():
                conn = await self._pool.get()
                await conn.close()
            for conn in list(self._used):
                await conn.close()
            self._used.clear()

    async def ping(self) -> bool:
        try:
            conn = await self.acquire()
            await conn.connect()
            future = await conn.send("ping_topic", b"ping")
            _ = await future
            await self.release(conn)
            return True
        except Exception:
            return False

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[KafkaProducerConnection, None]:
        conn = await self.acquire()
        self._used.add(conn)
        try:
            yield conn
        finally:
            await self.release(conn)
