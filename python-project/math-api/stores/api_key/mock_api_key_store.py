import asyncio
from fastapi import Depends

from stores.api_key.base_api_key_store import BaseApiKeyStore

class MockApiKeyStore(BaseApiKeyStore):
    def __init__(self):
        self.api_key: str = "mysecretkey"

    async def is_valid_key(self, key: str) -> bool:
        await asyncio.sleep(1)  # Simulate async operation
        return key == self.api_key
