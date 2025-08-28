from typing import List

from domain.repositories.interfaces import IChatEventRepository
from domain.entities.conversation_events.conversation_event import ConversationEvent

class InMemoryChatEventRepository(IChatEventRepository):
    def __init__(self):
        self.events: List[ConversationEvent] = []

    async def create_event(self, event: ConversationEvent) -> ConversationEvent:
        event.id = len(self.events) + 1
        self.events.append(event)
        return event

    async def list_events_by_chat(
        self, 
        chat_id: int
    ) -> List[ConversationEvent]:
        events = [event for event in self.events if event.chat_id == chat_id]
        return events
