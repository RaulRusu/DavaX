# shared_core/kafka/retry_strategies.py

import asyncio

async def forever_retry_strategy(attempt: int, exc: Exception) -> bool:
    print(f"Send/connect failed {attempt} times: {exc}")
    await asyncio.sleep(min(60, 2 ** min(attempt, 6)))  # Exponential backoff, max 60s
    return True

def max_attempts_strategy_factory(max_attempts: int = 5):
    async def strategy(attempt: int, exc: Exception) -> bool:
        print(f"Attempt {attempt}/{max_attempts} failed: {exc}")
        await asyncio.sleep(2 ** min(attempt, 6))
        return attempt < max_attempts
    return strategy
