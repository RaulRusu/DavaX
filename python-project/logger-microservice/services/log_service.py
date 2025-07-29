from typing import Optional
from shared_core.models.service_log import ServiceLog
from asyncio import create_task
from stores.log_store import ServiceLogStore
class LogService:
    def __init__(self, log_store: ServiceLogStore):
        self.log_store = log_store

    async def write_log(self, log: ServiceLog) -> bool:
        return await self.log_store.save(log)

class LogProcessor:
    def __init__(self, log_service: LogService):
        self.log_service = log_service

    async def __call__(self, message: str) -> None:
        print("Received log message: ", message)
        log: Optional[ServiceLog] = None
        if not message:
            return
        try:
            log = ServiceLog.model_validate_json(message)
        except Exception as e:
            print(f"Failed to parse log message: {e}")
            return

        create_task(self.log_service.write_log(log))