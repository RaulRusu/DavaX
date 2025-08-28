"""
Handles the multi-step loop: send prompt → model may emit function_call(s) →
execute tools → append outputs → repeat until no more calls or max_steps.
"""

import json
from typing import List, Dict, Callable, Awaitable, Tuple, Any

import openai

from infrastructure.llm.openai_chat import OpenAIChat

from openai.types.responses import ResponseOutputItem

def aggregate_output_text(output: List[ResponseOutputItem]) -> str:
    """Aggregate plain text content from a Response output array."""
    parts = []
    for it in output:
        if it.type == "message":
            for block in it.content:
                if getattr(block, "type", None) == "output_text":
                    parts.append(block.text)
    return "".join(parts)

async def run_tool_loop(
    llm_client: OpenAIChat,
    input_items: List[Dict],
    on_function_call: Callable[[Dict], Awaitable[None]],
    on_function_call_output: Callable[[str, str, Any], Awaitable[None]],
    on_exception: Callable[[Exception], Awaitable[None]] = None,
    max_steps: int = 3,
) -> Tuple[str, Any]:
    """
    Args:
        llm_client: object with .generate_response(input_items, tools=tools) -> Response
        input_items: initial LLM input (list of dicts)
        tools: list of function specs (schemas)
        on_function_call: async callback for each function call (persist)
        on_function_result: async callback for each tool result (persist)
        max_steps: max tool-calling loops allowed

    Returns:
        (final_text, last_response)
    """
    try:
        all_text = []
        resp = await llm_client.generate_response(input_items)
        step = 0

        while step < max_steps:
            step += 1

            all_text.append(aggregate_output_text(resp.output))

            # collect tool calls
            calls = []
            for it in resp.output or []:
                if it.type == "function_call":
                    calls.append(it)

            if not calls:
                break

            outputs = []
            for call in calls:
                await on_function_call(call)
                object_args = json.loads(call.arguments)
                tool_result = await llm_client.call_tool(call.name, object_args)
                await on_function_call_output(call.call_id, call.name, tool_result, object_args)
                outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(tool_result)
                })

            input_items = input_items + calls + outputs
            resp = await llm_client.generate_response(input_items)

        return "".join(all_text), resp
    except openai.RateLimitError as e:
        if on_exception:
            await on_exception(e)
        return f"An error occurred: {e}", None