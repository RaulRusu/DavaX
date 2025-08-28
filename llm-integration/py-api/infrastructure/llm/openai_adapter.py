from domain.entities.message.message import (
    TextMessage,
    FunctionCallMessage,
    FunctionResponseMessage,
    MessageBase,
)

from infrastructure.llm.function import LLMFunction, Param, JSON_TYPE_MAP

from typing import Dict, Any, List, Type

def export_text_message(msg: TextMessage) -> Dict[str, Any]:
    return {
        "role": msg.role,
        "content": msg.content,
    }

def export_function_call_message(msg: FunctionCallMessage) -> Dict[str, Any]:
    return {
        "role": "function_call",
        "name": msg.name,
        "arguments": msg.arguments,
    }

def export_function_response_message(msg: FunctionResponseMessage) -> Dict[str, Any]:
    return {
        "role": "function_call_output",
        "name": getattr(msg, "name", None),  
        "content": msg.output,
    }

EXPORTER_MAP: Dict[Type[MessageBase], callable] = {
    TextMessage: export_text_message,
    FunctionCallMessage: export_function_call_message,
    FunctionResponseMessage: export_function_response_message,
}

def pydantic_to_openai(message: MessageBase) -> Dict[str, Any]:
    exporter = EXPORTER_MAP.get(type(message))
    if exporter is None:
        raise ValueError(f"No OpenAI exporter for type: {type(message)}")
    return exporter(message)

def bulk_pydantic_to_openai(messages: list[MessageBase]) -> list[Dict[str, Any]]:
    return [pydantic_to_openai(msg) for msg in messages]

def function_params_to_open(params: List[Param]) -> Dict[str, Any]:
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

def function_to_openai(function: LLMFunction) -> Dict[str, Any]:
    return {
        "type": "function",
        "name": function.name,
        "description": function.description,
        "parameters": function_params_to_open(function.params)
    }