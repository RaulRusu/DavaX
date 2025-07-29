from fastapi import Depends
from stores import store_provider

from services.math_service import MathService
from services.request_record_service import RequestRecordService
from stores.request_record_store import RequestRecordStore
from services.health_service import HealthService
from shared_core.di.container import container
from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.kafka.sender import KafkaProducerConnectionPool

async def get_math_service() -> MathService:
    return MathService()

async def get_request_record_service() -> RequestRecordService:
    request_record_store = await store_provider.get_request_record_store()
    return RequestRecordService(request_record_store=request_record_store)

async def get_health_service() -> HealthService:
    db_client = await container.resolve(OracleDBClient)
    kafka_pool = await container.resolve(KafkaProducerConnectionPool)
    return HealthService(db_client, kafka_pool)