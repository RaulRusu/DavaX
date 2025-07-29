from typing import Optional
from pydantic import BaseModel

class RequestRecord(BaseModel):
    api_key: Optional[str]
    endpoint: str
    request_method: str
    request_input: dict
    request_status: str