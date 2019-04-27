from __future__ import annotations

from asyncio import get_running_loop
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

T = TypeVar('T')
utc = timezone.utc


def timestamp_key(timestamp: datetime) -> str:
    """
    Get the key under which the timestamp is stored in a collection.
    Supposed to be monotonic (non-decreasing).
    """
    return timestamp.astimezone(utc).strftime('%Y%m%d%H%M%S%f')


async def run_in_executor(callable_: Callable[..., T], *args: Any) -> T:
    return get_running_loop().run_in_executor(None, callable_, *args)


async def setattr_async(object_: Any, attribute: Any, value: Any):
    await run_in_executor(setattr, object_, attribute, value)
