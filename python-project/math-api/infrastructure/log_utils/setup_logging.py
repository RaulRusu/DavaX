import logging

from infrastructure.config import ServiceConfig
from infrastructure.log_utils.kafka_handler import KafkaLoggingHandler
from shared_core.kafka.log_dispatcher import KafkaLogDispatcher
from shared_core.di.container import container 

async def setup_logging() -> None:
    logger_error = logging.getLogger('uvicorn.error')
    logger_access = logging.getLogger('uvicorn.access')
    log_dispatcher = await container.resolve(KafkaLogDispatcher)
    service_config = await container.resolve(ServiceConfig)

    kafka_logging_handler = KafkaLoggingHandler(
        kafka_log_dispatcher=log_dispatcher,
        svc_name=service_config.svc_name,
        svc_host=service_config.svc_host
    )

    logger_error.addHandler(kafka_logging_handler)
    logger_access.addHandler(kafka_logging_handler)

async def clear_logging() -> None:
    logger_error = logging.getLogger('uvicorn.error')
    logger_access = logging.getLogger('uvicorn.access')

    for handler in logger_error.handlers[:]:
        if isinstance(handler, KafkaLoggingHandler):
            logger_error.removeHandler(handler)

    for handler in logger_access.handlers[:]:
        if isinstance(handler, KafkaLoggingHandler):
            logger_access.removeHandler(handler)