from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Chat(BaseModel):
    id: Optional[int] = Field(None, example=456)
    client_id: str = Field(..., example="client-123")
    title: Optional[str] = Field(None, example="My chat")
    created_at: datetime = Field(None, example="2023-10-01T12:00:00Z")
    last_active_at: datetime = Field(None, example="2023-10-02T12:34:56Z")

