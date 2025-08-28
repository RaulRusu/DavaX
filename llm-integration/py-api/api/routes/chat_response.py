from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from application.llm.tool_registry import OpenAIToolsRegistry
from application.llm.view_builder import OpenAIViewBuilder
from application.rag.pipeline import RAGPipeline
from application.rag.rag_router import get_rag_router
from application.services.llm_chat_service import LLMChatService

from domain.repositories.chat_event_repo import InMemoryChatEventRepository
from domain.repositories.client_repo import InMemoryClientRepository
from domain.repositories.chat_repo import InMemoryChatRepository

from domain.entities.client.client import Client
from domain.entities.chat.chat import Chat
from domain.entities.conversation_events.conversation_event import ConversationEvent

from infrastructure.llm.openai_chat import OpenAIChat
from infrastructure.di.container import container
from application.functions.summary_function import get_summary_tool

from api.dto.models import CreateClientIn, CreateChatIn, ChatInput

load_dotenv(".env")

router = APIRouter()

client_repo = InMemoryClientRepository()
chat_repo = InMemoryChatRepository()
event_repo = InMemoryChatEventRepository()

tools_registry = OpenAIToolsRegistry()
tools_registry.register(get_summary_tool())

llm_client = OpenAIChat(
    tools_registry=tools_registry
)

view_builder = OpenAIViewBuilder()
rag_router = get_rag_router()

# ----- wiring -----
async def get_llm_chat_service() -> LLMChatService:
    rag = await container.resolve(RAGPipeline)
    return LLMChatService(
        client_repo,
        chat_repo,
        event_repo,
        llm_client,
        view_builder,
        rag,
        rag_router
    )


# -------- Clients --------
@router.post("/clients", response_model=Client)
async def create_client(payload: CreateClientIn):
    return await client_repo.create_client(payload.client_id)


@router.get("/clients/{client_id}", response_model=Client)
async def get_client(client_id: str):
    client = await client_repo.get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


# -------- Chats --------
@router.post("/chats", response_model=Chat)
async def create_chat(payload: CreateChatIn):
    chat = Chat(client_id=payload.client_id, title=payload.title)
    return await chat_repo.create_chat(chat)


@router.get("/clients/{client_id}/chats", response_model=List[Chat])
async def list_chats(client_id: str):
    return await chat_repo.list_chats_by_client(client_id)


@router.get("/chats/{chat_id}", response_model=Chat)
async def get_chat(chat_id: int):
    chat = await chat_repo.get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


# -------- Messages --------
@router.get("/chats/{chat_id}/messages", response_model=List[ConversationEvent])
async def get_chat_history(
    chat_id: int,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service)):
    return await event_repo.list_events_by_chat(chat_id)


# -------- Chat with LLM (round-trip) --------
@router.post("/chats/{chat_id}/messages", response_model=ConversationEvent)
async def chat_with_llm(
    chat_id: int,
    payload: ChatInput,
    llm_chat_service: LLMChatService = Depends(get_llm_chat_service),
):
    reply: ConversationEvent = await llm_chat_service.send_message(
        chat_id, payload.user_message
    )
    return reply
