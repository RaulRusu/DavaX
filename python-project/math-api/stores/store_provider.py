from fastapi import Depends

from stores.api_key.base_api_key_store import BaseApiKeyStore
from stores.api_key.db_api_key_store import DBApiKeyStore
from stores.request_record_store import RequestRecordStore

from shared_core.db.oracle_db_client import OracleDBClient 
from shared_core.di.container import container

async def get_api_key_store() -> BaseApiKeyStore:
    db_client = await container.resolve(OracleDBClient)
    return DBApiKeyStore(db_client)

async def get_request_record_store() -> RequestRecordStore:
    db_client = await container.resolve(OracleDBClient)
    return RequestRecordStore(db_client)