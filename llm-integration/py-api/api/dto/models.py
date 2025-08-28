# routes/models.py
from typing import Annotated, Union, Optional
from pydantic import BaseModel, Field

from domain.entities.message.message import (
    TextMessage,
    FunctionCallMessage,
    FunctionResponseMessage,
)

# JSON bodies for creates / chat input
class CreateClientIn(BaseModel):
    client_id: str

class CreateChatIn(BaseModel):
    client_id: str
    title: Optional[str] = None

class ChatInput(BaseModel):
    user_message: str

# Discriminated union so FastAPI returns full variant payloads
MessageAny = Annotated[
    Union[TextMessage, FunctionCallMessage, FunctionResponseMessage],
    Field(discriminator="message_type"),
]
