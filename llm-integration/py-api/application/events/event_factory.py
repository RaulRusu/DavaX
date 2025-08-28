from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from domain.entities.conversation_events.conversation_event import ConversationEvent
from domain.value_objects.roles import Role
from domain.value_objects.event_types import EventType


def _now():
    return datetime.now(timezone.utc)


def user_message(chat_id: int, text: str) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.USER,
        event_type=EventType.MESSAGE_TEXT,
        created_at=_now(),
        payload={"content": text},
    )


def assistant_message(chat_id: int, text: str) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.ASSISTANT,
        event_type=EventType.MESSAGE_TEXT,
        created_at=_now(),
        payload={"content": text},
    )


def system_message(chat_id: int, text: str) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.SYSTEM,
        event_type=EventType.MESSAGE_TEXT,
        created_at=_now(),
        payload={"content": text},
    )


def developer_message(chat_id: int, text: str) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.DEVELOPER,
        event_type=EventType.MESSAGE_TEXT,
        created_at=_now(),
        payload={"content": text},
    )


def function_call(chat_id: int, name: str, call_id: str,
                  arguments: Dict[str, Any],
                  original_id: Optional[str] = None) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.EVENT,
        event_type=EventType.FUNCTION_CALL,
        created_at=_now(),
        payload={
            "name": name,
            "call_id": call_id,
            "arguments": arguments,
            "original_id": original_id,
        },
    )


def function_result(chat_id: int, call_id: str,
                    output: Any,
                    arguments: Dict[str, Any],
                    name: Optional[str] = None) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.EVENT,
        event_type=EventType.FUNCTION_CALL_OUTPUT,
        created_at=_now(),
        payload={
            "name": name,
            "call_id": call_id,
            "output": output,
            "arguments": arguments
        },
    )


def rag_query(chat_id: int, query: str, filters: Optional[Dict[str, Any]] = None) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.EVENT,
        event_type=EventType.RAG_QUERY,
        created_at=_now(),
        payload={"query": query, "filters": filters or {}},
    )


def rag_retrieval(chat_id: int, results: list) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.EVENT,
        event_type=EventType.RAG_RETRIEVAL,
        created_at=_now(),
        payload={"results": results},
    )


def rag_summary(chat_id: int, picks: List[Dict[str, str]]) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.DEVELOPER,
        event_type=EventType.RAG_SUMMARY,
        created_at=_now(),
        payload={"picks": picks},
    )

def error_event(chat_id: int, error_message: str) -> ConversationEvent:
    return ConversationEvent(
        chat_id=chat_id,
        role=Role.EVENT,
        event_type=EventType.ERROR,
        created_at=_now(),
        payload={"error": error_message},
    )
