from fastapi import Security, HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader

from stores import store_provider
from stores.api_key.base_api_key_store import BaseApiKeyStore

API_KEY_NAME = "x-api-key"

async def get_api_key(
    api_key_header: str = Security(APIKeyHeader(name=API_KEY_NAME, auto_error=False)),
    api_key_store: BaseApiKeyStore = Depends(store_provider.get_api_key_store)
):
    if not await api_key_store.is_valid_key(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing API key",
        )
    return api_key_header