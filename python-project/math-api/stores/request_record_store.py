import asyncio
from typing import Optional

import oracledb
from shared_core.db.oracle_db_client import OracleDBClient
from models.request_record import RequestRecord
import oracledb.exceptions as oracle_exceptions


class RequestRecordStore:
    def __init__(self, db_client: OracleDBClient):
        self.db_client = db_client

    async def save(self, request_record: RequestRecord):
        connection: Optional[oracledb.AsyncConnection] = None
        try:
            connection = await self.db_client.acquire()
            with connection.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO api_request_records (api_key, endpoint, request_method, request_input, request_status) VALUES (:api_key, :endpoint, :request_method, :request_input, :request_status)",
                    {
                        "api_key": request_record.api_key,
                        "endpoint": request_record.endpoint,
                        "request_method": request_record.request_method,
                        "request_input": str(request_record.request_input),
                        "request_status": request_record.request_status
                    }
                )
                await connection.commit()
        except asyncio.TimeoutError:
            self.db_client.logger.error("Database connection timed out!")
        except Exception as e:
            self.db_client.logger.error(f"Some other error: {e}")
            return False
        finally:
            if connection:
                await self.db_client.release(connection)
        return True
            
