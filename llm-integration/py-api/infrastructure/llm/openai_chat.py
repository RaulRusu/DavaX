from datetime import datetime, timezone
from typing import Callable, List, Dict, Any, Optional
from openai import AsyncOpenAI
from openai.types.responses import Response
from application.llm.tool_registry import ToolsRegistry
from domain.entities.conversation_events.conversation_event import ConversationEvent

class OpenAIChat():
    def __init__(
            self,
            model: str = "gpt-4.1-nano", 
            tools_registry: ToolsRegistry = None):
        self.client = AsyncOpenAI()
        self.model = model
        self.tools_registry = tools_registry

    async def generate_response(self, messages: List, **kwargs) -> Response:
        response: Response = await self.client.responses.create(
            model=self.model,
            input=messages,
            tools=[specs for specs in self.tools_registry.specs()] if self.tools_registry else None,
            **kwargs
        )
        return response

    async def call_tool(self, tool_name: str, args) -> Any:
        if not self.tools_registry:
            raise ValueError("No tools registry available")
        
        return self.tools_registry.run(tool_name, args)