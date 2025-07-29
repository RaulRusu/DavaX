from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ServiceLog(BaseModel):
    log_timestamp: datetime = Field(..., description="UTC timestamp when the log was created")
    log_level: str = Field(..., description="Log level, e.g. INFO, ERROR")
    logger_name: str = Field(..., description="Name of the logger/module")
    log_message: str = Field(..., description="The log message itself")
    svc_name: str = Field(..., description="Name of the service emitting the log")
    svc_host: Optional[str] = Field(None, description="Host or container where the service runs")