import oracledb
import asyncio
from shared_core.config.env_loader import get_db_config

class OracleDBClient:
    def __init__(self):
        config = get_db_config()
        self.user: str = config.db_user
        self.password: str = config.db_password
        self.dsn: str = config.db_dsn
        self.pool = None

    def create_pool(self):
        if self.pool is None:
            self.pool = oracledb.create_pool_async(
                user=self.user,
                password=self.password,
                dsn=self.dsn,
                min=1,
                max=4,
                increment=1,
                getmode=oracledb.SPOOL_ATTRVAL_WAIT
            )

    async def acquire(self, timeout = 1) -> oracledb.AsyncConnection:
        return await asyncio.wait_for(self.pool.acquire(), timeout=timeout)

    async def release(self, connection):
        await self.pool.release(connection)

    async def close_pool(self):
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    async def ping(self) -> bool:
        try:
            connection = await self.acquire()
            async with connection.cursor() as cursor:
                await cursor.execute("SELECT 1 FROM dual")
                _ = await cursor.fetchone()
                return True
        except Exception as e:
            print(f"Database ping failed: {e}")
            return False
