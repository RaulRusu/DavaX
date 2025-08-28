from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from domain.entities.client.client import Client
from domain.entities.chat.chat import Chat
from domain.entities.message.message import MessageBase
from domain.entities.conversation_events.conversation_event import ConversationEvent

class IClientRepository(ABC):
    @abstractmethod
    async def create_client(self, client_id: str) -> Client:
        ...

    @abstractmethod
    async def get_client(self, client_id: str) -> Optional[Client]:
        ...


class IChatRepository(ABC):
    @abstractmethod
    async def create_chat(self, chat: Chat) -> Chat:
        ...

    @abstractmethod
    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        ...

    @abstractmethod
    async def list_chats_by_client(self, client_id: str) -> List[Chat]:
        ...


class IMessageRepository(ABC):
    @abstractmethod
    async def create_message(self, message: MessageBase) -> MessageBase:
        ...

    @abstractmethod
    async def list_messages_by_chat(
        self, 
        chat_id: str, 
        since: Optional[datetime] = None
    ) -> List[MessageBase]:
        ...

class IChatEventRepository(ABC):
    @abstractmethod
    async def create_event(self, event: ConversationEvent) -> ConversationEvent:
        ...

    @abstractmethod
    async def list_events_by_chat(
        self, 
        chat_id: str
    ) -> List[ConversationEvent]:
        ...
