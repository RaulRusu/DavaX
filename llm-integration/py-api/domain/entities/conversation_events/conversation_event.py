from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

class ConversationEvent(BaseModel):
    id: Optional[int] = Field(None, example=123)
    chat_id: Optional[int] = Field(None, example=456)
    role: Optional[str] = Field(None, example="user")
    event_type: Optional[str] = Field(None, example="message")
    content: Optional[Dict[str, str]] = Field(None, example={"raw": "Hello, pass!{", "masked": "Hello, [PASS]!}"})
    visibility: Optional[List[str]] = Field(None, example=["user", "llm_input", "audit"])
    created_at: Optional[datetime] = Field(None, example="2023-01-01T00:00:00Z")
    payload: Optional[Dict] = Field(None, example={"content": "Hello, world!"})

        