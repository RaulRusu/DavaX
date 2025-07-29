from typing_extensions import Protocol


class RetryStrategy(Protocol):
    async def __call__(self, attempt: int, exception: Exception) -> bool: ...