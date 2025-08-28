import asyncio
import json
import random
from typing import List

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException

from application.llm.tool_registry import OpenAIToolsRegistry
from application.llm.view_builder import OpenAIViewBuilder
from application.rag.rag_router import get_rag_router
from application.services.llm_chat_service import LLMChatService

from domain.repositories.chat_event_repo import InMemoryChatEventRepository
from domain.repositories.client_repo import InMemoryClientRepository
from domain.repositories.chat_repo import InMemoryChatRepository

from domain.entities.client.client import Client
from domain.entities.chat.chat import Chat
from domain.entities.conversation_events.conversation_event import ConversationEvent

from infrastructure.llm.function import LLMFunction, Param
from infrastructure.llm.openai_chat import OpenAIChat
from application.functions.summary_function import get_summary_tool

from infrastructure.vectorstore import indexer_worker

load_dotenv(".env")

client_repo = InMemoryClientRepository()
chat_repo = InMemoryChatRepository()
event_repo = InMemoryChatEventRepository()

tools_registry = OpenAIToolsRegistry()
tools_registry.register(get_summary_tool())

def bob(title: str) -> str:
    return "Gatsby the great hacker of 1919"

get_book_characters_tool = LLMFunction(
    name="get_book_characters",
    description="Get characters of a book",
    handler=bob,
    params=[Param("title", str, "Exact book title", required=True)]
)

tools_registry.register(get_book_characters_tool)

llm_client = OpenAIChat(
    tools_registry=tools_registry
)

view_builder = OpenAIViewBuilder()

indexer_worker.run_sync()

from application.rag.pipeline import RAGPipeline

rag = RAGPipeline()
rag.init_blocking()

rag_router = get_rag_router()

async def print_rag_result():
    print(await rag_router.should_rag("can you recommend me a book that is like 'Pride and Prejudice'?"))

asyncio.run(print_rag_result())
exit()
# ----- wiring -----
def get_llm_chat_service() -> LLMChatService:
    return LLMChatService(client_repo, chat_repo, event_repo, llm_client, view_builder, rag)

async def main():
    chat_service = get_llm_chat_service()
    response = await chat_service.send_message(1, "can you recomand me a book about romance and war?")
    history = await event_repo.list_events_by_chat(1)
    print(history)
    # while True:
    #     user_input = input("You: ")
    #     if user_input.lower() == "exit":
    #         break
    #     resp = await chat_service.send_message(1, user_input)



# rag_result = rag.retrieve("recommend me a romance book")
# print("RAG Result:", json.dumps(rag_result))
# exit()
asyncio.run(main())