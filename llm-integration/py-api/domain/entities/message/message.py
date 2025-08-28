from pydantic import BaseModel, Field, model_validator
from typing import Dict, Any, Literal, Optional
from datetime import datetime

class MessageBase(BaseModel):
    id: Optional[int] = Field(None, example=123)
    chat_id: int = Field(..., example=456)
    created_at: datetime = Field(..., example="2023-10-01T12:00:00Z")

class TextMessage(MessageBase):
    role: str = Field(..., example="user")
    content: str = Field(..., example="What is my horoscope? I am an Aquarius.")
    message_type: Literal["text"] = "text"

class FunctionCallMessage(MessageBase):
    call_id: str = Field(..., example="call_BcMqVrypc1FE887pA6lH5zGA")
    name: str = Field(..., example="get_horoscope")
    arguments: Dict[str, Any] = Field(..., example={"sign": "Aquarius"})
    message_type: Literal["function_call"] = "function_call"

class FunctionResponseMessage(MessageBase):
    call_id: str = Field(..., example="call_BcMqVrypc1FE887pA6lH5zGA")
    output: Dict[str, Any] = Field(..., example={"horoscope": "Aquarius: Tomorrow is lucky."})
    message_type: Literal["function_call_output"] = "function_call_output"