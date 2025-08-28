import json
from pathlib import Path
from infrastructure.config import settings
from infrastructure.llm.openai_chat import OpenAIChat


class RagRouter:
    def __init__(self, llm_client: OpenAIChat, system_prompt: str):
        self.llm_client = llm_client
        self.system_prompt = system_prompt

    async def should_rag(self, user_text: str) -> dict:
        """
        Call the router LLM and return JSON like:
        {
          "should_rag": bool,
          "tags": list[str]
        }
        """
        try:

            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_text}
            ]
            response = await self.llm_client.generate_response(
                messages=messages
            )
            return json.loads(response.output_text)
        except Exception as e:
            print(f"Error in RagRouter: {e}")
            return {
                "should_rag": False,
                "tags": []
            }

def get_rag_router() -> RagRouter:
    llm_client = OpenAIChat()
    #load system prompt from file
    system_prompt_path = Path(settings.ROUTER_SYSTEM_PROMPT_PATH)
    system_prompt = system_prompt_path.read_text(encoding="utf-8")
    return RagRouter(llm_client=llm_client, system_prompt=system_prompt)

