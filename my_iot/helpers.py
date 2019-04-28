from __future__ import annotations

from asyncio import get_running_loop
from functools import partial
from typing import Any, Callable, TypeVar

T = TypeVar('T')


async def run_in_executor(callable_: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    return await get_running_loop().run_in_executor(None, partial(callable_, *args, **kwargs))
