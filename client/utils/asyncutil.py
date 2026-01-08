import asyncio
from typing import Callable, Any


def run_sync(coro):
    """Run coroutine synchronously"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    
    # Already in async context create task
    return asyncio.create_task(coro)


def make_async(func: Callable) -> Callable:
    """Convert sync function to async"""
    async def wrapper(*args, **kwargs) -> Any:
        return func(*args, **kwargs)
    return wrapper
