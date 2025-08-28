from typing import List, Optional
from datetime import datetime, timezone

from domain.repositories.interfaces import IChatRepository
from domain.entities.chat.chat import Chat

class InMemoryChatRepository(IChatRepository):
    def __init__(self):
        self.chats = {}

    async def create_chat(self, chat: Chat) -> Chat:
        chat.id = len(self.chats) + 1
        chat.created_at = datetime.now(timezone.utc)
        chat.last_active_at = datetime.now(timezone.utc)
        self.chats[chat.id] = chat
        return chat

    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        return self.chats.get(chat_id)

    async def list_chats_by_client(self, client_id: str) -> List[Chat]:
        return [chat for chat in self.chats.values() if chat.client_id == client_id]