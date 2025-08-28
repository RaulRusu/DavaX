from abc import ABC, abstractmethod
from typing import Any, List
from domain.entities.message.message import MessageBase

class LLMClientBase(ABC):
    @abstractmethod
    async def generate_response(self, messages: List[MessageBase], chat_id: int, **kwargs) -> List[MessageBase]:
        """
        Generate a response from the LLM given a list of messages.
        :param messages: List of dicts in the format required by the LLM.
        :return: The response from the LLM (raw or processed).
        """
        pass
