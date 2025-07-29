import asyncio
from typing import Optional

import oracledb
from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.models.service_log import ServiceLog
import oracledb.exceptions as oracle_exceptions

class ServiceLogStore:
    def __init__(self, db_client: OracleDBClient):
        self.db_client = db_client

    async def save(self, service_log: ServiceLog):
        connection: Optional[oracledb.AsyncConnection] = None
        try:
            connection = await self.db_client.acquire()
            async with connection.cursor() as cursor:
                await cursor.execute(
                    """
                    INSERT INTO service_logs (
                        log_timestamp,
                        log_level,
                        logger_name,
                        log_message,
                        svc_name,
                        svc_host
                    ) VALUES (
                        :log_timestamp,
                        :log_level,
                        :logger_name,
                        :log_message,
                        :svc_name,
                        :svc_host
                    )
                    """,
                    {
                        "log_timestamp": service_log.log_timestamp,
                        "log_level": service_log.log_level,
                        "logger_name": service_log.logger_name,
                        "log_message": service_log.log_message,
                        "svc_name": service_log.svc_name,
                        "svc_host": service_log.svc_host,
                    }
                )
                await connection.commit()
        except asyncio.TimeoutError:
            print("Database connection timed out!")
            # TODO: add proper logging
            return False
        except Exception as e:
            print("Database error:", e)
            # TODO: add proper logging
            return False
        finally:
            if connection:
                await self.db_client.release(connection)
        return True
