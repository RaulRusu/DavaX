"""
view_registry.py
----------------
Registry for mapping ConversationEvents into LLM input items.
Each mapper is just a function: (ConversationEvent) -> List[Dict]
"""

from __future__ import annotations
from typing import List, Dict, Optional, Callable
from datetime import datetime
import json

from domain.entities.conversation_events.conversation_event import ConversationEvent
from domain.value_objects.roles import Role
from domain.value_objects.event_types import EventType


# Registry 

EventMapper = Callable[[ConversationEvent], List[Dict]]

class ViewBuilder:
    def __init__(self):
        self._mappers: Dict[str, EventMapper] = {}

    def register(self, event_type: str, mapper: EventMapper):
        self._mappers[event_type] = mapper

    def get(self, event_type: Optional[str]) -> Optional[EventMapper]:
        return self._mappers.get(event_type or "")

    def build_input(
        self,
        events: List[ConversationEvent],
        *,
        include_system_prefix: Optional[str] = None
    ) -> List[Dict]:
        items: List[Dict] = []

        if include_system_prefix:
            items.append({"role": "system", "content": include_system_prefix})

        for event in events:
            mapper = self.get(event.event_type)
            if not mapper:
                continue
            items.extend(mapper(event))

        return items

# OpenAI mappers

def message_text_mapper(event: ConversationEvent) -> List[Dict]:
    text = event.payload.get("content", "") if event.payload else ""
    if not text:
        return []
    role = event.role or Role.USER
    return [{"role": role, "content": text}]


def summary_mapper(event: ConversationEvent) -> List[Dict]:
    text = event.payload.get("content", "") if event.payload else ""
    if not text:
        return []
    return [{"role": "system", "content": text}]


def rag_summary_mapper(event: ConversationEvent) -> List[Dict]:
    picks = event.payload.get("picks", []) if event.payload else []
    if not picks:
        return []
    text = "\n".join(f"- {pick.get('title', '')} -> {pick.get('tags', '')}" for pick in picks)
    return [{"role": "developer", "content": f"Context: RagSummary\n{text}"}]


def function_result_mapper(event: ConversationEvent) -> List[Dict]:
    payload = event.payload or {}
    name = payload.get("name") or "tool"
    args = payload.get("arguments", {})
    output = payload.get("output", "")
    call_str = f"Memory: {name}({json.dumps(args, ensure_ascii=False)})"
    return [{"role": "developer", "content": f"{call_str} => {output}"}]


# OpenAI registry wiring

class OpenAIViewBuilder(ViewBuilder):
    def __init__(self):
        super().__init__()
        self.register(EventType.MESSAGE_TEXT, message_text_mapper)
        self.register(EventType.SUMMARY, summary_mapper)
        self.register(EventType.RAG_SUMMARY, rag_summary_mapper)
        self.register(EventType.FUNCTION_CALL_OUTPUT, function_result_mapper)
