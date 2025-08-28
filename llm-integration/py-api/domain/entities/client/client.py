from pydantic import BaseModel, Field
from datetime import datetime

class Client(BaseModel):
    id: str = Field(..., example="client-123")
    created_at: datetime = Field(..., example="2023-10-01T12:00:00Z")

class ClientIn(BaseModel):
    id: str = Field(..., example="client-123")