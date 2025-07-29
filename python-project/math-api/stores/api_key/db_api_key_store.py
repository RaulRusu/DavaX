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
            print("Database connection timed out!")
            #TODO: add proper logging
        except Exception as e:
            print("Some other error:", e)
            #TODO: add proper logging
            return False
        finally:
            if connection:
                await self.db_client.release(connection)