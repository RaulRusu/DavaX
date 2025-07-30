import asyncio

async def forever_retry_strategy(attempt: int) -> bool:
    await asyncio.sleep(min(60, 2 ** min(attempt, 6)))  # Exponential backoff, max 60s
    return True

def max_attempts_strategy_factory(max_attempts: int = 5):
    async def strategy(attempt: int) -> bool:
        await asyncio.sleep(2 ** min(attempt, 6))
        return attempt < max_attempts
    return strategy
