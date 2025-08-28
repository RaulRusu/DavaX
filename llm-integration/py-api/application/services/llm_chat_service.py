import json
from typing import List
from datetime import datetime, timezone

from openai.types.responses import ResponseFunctionToolCall, Response

from application.rag.pipeline import RAGPipeline
from application.rag.rag_router import RagRouter
from infrastructure.config import settings

from application.llm.view_builder import ViewBuilder
from domain.repositories.interfaces import IChatEventRepository, IChatRepository, IClientRepository

from domain.entities.conversation_events.conversation_event import ConversationEvent
from infrastructure.llm.openai_chat import OpenAIChat
from application.events import event_factory
from application.llm.tool_loop import run_tool_loop

class LLMChatService:
    def __init__(self, 
        client_repo: IClientRepository,
        chat_repo: IChatRepository,
        event_repo: IChatEventRepository,
        llm_client: OpenAIChat,
        view_builder: ViewBuilder,
        rag_pipeline: RAGPipeline,
        rag_router: RagRouter
        ):
        self.llm_client = llm_client
        self.client_repo = client_repo
        self.chat_repo = chat_repo
        self.event_repo = event_repo
        self.view_builder = view_builder
        self.rag_pipeline = rag_pipeline
        self.rag_router = rag_router

    async def send_message(self, chat_id: int, user_text: str):
        # 1. Persist user message
        user_message_event = event_factory.user_message(chat_id, user_text)
        await self.event_repo.create_event(user_message_event)

        # 2. RAG
        rag_query = await self.rag_router.should_rag(user_text)
        if rag_query.get("should_rag", False):
            rag_output = self.rag_pipeline.retrieve(" ".join(rag_query["tags"]))

            # 2.2. Persist RAG events
            await self.event_repo.create_event(event_factory.rag_query(chat_id, rag_output["query"]))
            await self.event_repo.create_event(event_factory.rag_retrieval(chat_id, rag_output["full_results"]))
            await self.event_repo.create_event(event_factory.rag_summary(chat_id, rag_output["picks"]))

        # 3. Build input
        events = await self.event_repo.list_events_by_chat(chat_id)
        input_items = self.view_builder.build_input(events, include_system_prefix = settings.SYSTEM_MESSAGE)

        # 4. Tool Loop
        async def on_function_call(call):
            function_call_event = event_factory.function_call(
                chat_id=chat_id,
                name=call.name,
                arguments=json.loads(call.arguments),
                call_id=call.call_id,
                original_id=call.id
            )

            await self.event_repo.create_event(function_call_event)

        async def on_function_call_output(call_id, name, output, arguments):
            function_result_event = event_factory.function_result(
                chat_id=chat_id,
                call_id=call_id,
                output=output,
                arguments=arguments,
                name=name
            )
            await self.event_repo.create_event(function_result_event)

        async def on_exception(ex: Exception):
            error_event = event_factory.error_event(chat_id, str(ex))
            await self.event_repo.create_event(error_event)

        text, _ = await run_tool_loop(
            self.llm_client,
            input_items,
            on_function_call,
            on_function_call_output,
            on_exception=on_exception,
            max_steps=settings.TOOL_MAX_STEPS,
        )

        assistant_response_event = event_factory.assistant_message(chat_id, text)
        await self.event_repo.create_event(assistant_response_event)

        events = await self.event_repo.list_events_by_chat(chat_id)
        input_items = self.view_builder.build_input(events, include_system_prefix = settings.SYSTEM_MESSAGE)
        print(input_items, "\n\n")
        return assistant_response_event
