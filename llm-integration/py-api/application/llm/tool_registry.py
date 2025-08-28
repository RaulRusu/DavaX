"""
tools_registry.py
-----------------
Central registry of functions the LLM is allowed to call.
Each tool has: name, description, parameters schema, and a Python callable.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List
from infrastructure.llm.function import JSON_TYPE_MAP, LLMFunction, Param


class ToolsRegistry(ABC):
    def __init__(self):
        self._tools: Dict[str, LLMFunction] = {}

    def register(self, tool: LLMFunction):
        self._tools[tool.name] = tool

    def get(self, name: str) -> LLMFunction:
        return self._tools[name]

    @abstractmethod
    def specs(self) -> List[Dict[str, Any]]: ...

    def run(self, name: str, args: Dict[str, Any]):
        tool = self.get(name)

        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        return tool(**args)

class OpenAIToolsRegistry(ToolsRegistry):
    def __init__(self):
        super().__init__()

    def _function_params_to_open(self, params: List[Param]) -> Dict[str, Any]:
        properties = {}
        for param in params:
            properties[param.name] = {
                "type": JSON_TYPE_MAP.get(param.py_type),
                "description": param.description
            }
        return {
            "type": "object",
            "properties": properties,
            "required": [p.name for p in params if p.required]
        }

    def _function_to_openai(self, function: LLMFunction) -> Dict[str, Any]:
        return {
            "type": "function",
            "name": function.name,
            "description": function.description,
            "parameters": self._function_params_to_open(function.params)
        }

    def specs(self):
        for tool in self._tools.values():
            if isinstance(tool, LLMFunction):
                yield self._function_to_openai(tool)
