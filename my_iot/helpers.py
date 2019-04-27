from __future__ import annotations

from asyncio import get_running_loop
from datetime import datetime, timezone
from functools import partial, wraps
from typing import Awaitable, Callable, TypeVar

T = TypeVar('T')
utc = timezone.utc


def timestamp_key(timestamp: datetime) -> str:
    """
    Get the key under which the timestamp is stored in a collection.
    Supposed to be monotonic (non-decreasing).
    """
    return timestamp.astimezone(utc).strftime('%Y%m%d%H%M%S%f')


def run_in_executor(callable_: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    @wraps(callable_)
    async def wrapper(*args, **kwargs) -> T:
        return await get_running_loop().run_in_executor(None, partial(callable_, *args, **kwargs))
    return wrapper
