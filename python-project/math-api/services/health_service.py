from shared_core.db.oracle_db_client import OracleDBClient
from shared_core.kafka.sender.pool import KafkaProducerConnectionPool
import httpx

class HealthService:
    DOWN_STATUS = "DOWN"
    UP_STATUS = "UP"
    DEGRADED_STATUS = "DEGRADED"

    def __init__(self, db_client: OracleDBClient, producer_pool: KafkaProducerConnectionPool):
        self.db_client = db_client
        self.producer_pool = producer_pool

    async def check_log_microservice_health(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8001/health", timeout=2)
                return response.json()
        except httpx.RequestError as e:
            return {"status": HealthService.DOWN_STATUS}

    async def check_health(self):
        db_status = await self.db_client.ping()
        kafka_status = await self.producer_pool.ping()
        microservice_health = await self.check_log_microservice_health()

        db_state = HealthService.UP_STATUS if db_status else HealthService.DOWN_STATUS
        kafka_state = HealthService.UP_STATUS if kafka_status else HealthService.DOWN_STATUS

        status = HealthService.UP_STATUS
        if db_state == HealthService.DOWN_STATUS or kafka_state == HealthService.DOWN_STATUS:
            status = HealthService.DEGRADED_STATUS
        if microservice_health.get("status") == HealthService.DOWN_STATUS:
            status = HealthService.DEGRADED_STATUS

        return {
            "status": status,
            "details": {
                "db": {"status": db_state},
                "kafka": {"status": kafka_state},
                "log_microservice": microservice_health
            }
        }