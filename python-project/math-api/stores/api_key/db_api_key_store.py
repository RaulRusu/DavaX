import asyncio
from typing import Optional

import oracledb
from shared_core.db.oracle_db_client import OracleDBClient

from stores.api_key.base_api_key_store import BaseApiKeyStore

class DBApiKeyStore(BaseApiKeyStore):
    def __init__(self, db_client: OracleDBClient):
        self.db_client = db_client

    async def is_valid_key(self, key: str) -> bool:
        connection: Optional[oracledb.AsyncConnection] = None
        try:
            connection = await self.db_client.acquire()
            with connection.cursor() as cursor:
                await cursor.execute(f"SELECT 1 FROM api_keys WHERE api_key = :key", key=key)
                result = await cursor.fetchone()
                return result is not None
        except asyncio.TimeoutError:
            self.db_client.logger.error("Database connection timed out!")
        except Exception as e:
            self.db_client.logger.error(f"Some other error: {e}")
            return False
        finally:
            if connection:
                await self.db_client.release(connection)