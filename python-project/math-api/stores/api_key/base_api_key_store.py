from abc import ABC, abstractmethod

class BaseApiKeyStore(ABC):
    @abstractmethod
    async def is_valid_key(self, key: str) -> bool:
        pass