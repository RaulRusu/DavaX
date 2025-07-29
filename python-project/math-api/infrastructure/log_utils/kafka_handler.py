from logging import Handler, LogRecord
from asyncio import create_task
from shared_core.kafka.log_dispatcher import KafkaLogDispatcher
from shared_core.models.service_log import ServiceLog
from typing import Optional
from datetime import datetime, timezone

class KafkaLoggingHandler(Handler):
    def __init__(self, kafka_log_dispatcher: KafkaLogDispatcher, svc_name: str, svc_host: Optional[str] = None):
        super().__init__()
        self._dispatcher = kafka_log_dispatcher
        self._svc_name = svc_name
        self._svc_host = svc_host

    def log_record_to_service_log_json(
        self,
        record: LogRecord, 
        svc_name: str, 
        svc_host: Optional[str] = None
    ) -> str:
        log = ServiceLog(
            log_timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc),
            log_level = record.levelname,
            logger_name = record.name,
            log_message = record.getMessage(),
            svc_name = svc_name,
            svc_host = svc_host
        )
        return log

    def emit(self, record: LogRecord):
        msg = self.log_record_to_service_log_json(
            record, 
            self._svc_name, 
            self._svc_host
        )
        # If inside an async context, use:
        create_task(self._dispatcher.log(msg))