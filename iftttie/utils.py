from __future__ import annotations

from asyncio import Queue
from datetime import datetime
from types import ModuleType
from typing import AsyncIterable, TypeVar, Any

from aiohttp import StreamReader

T = TypeVar('T')


async def read_lines(reader: StreamReader) -> AsyncIterable[str]:
    """Provides async iterable interface for a reader."""
    while True:
        line: bytes = await reader.readline()
        if not line:
            break
        yield line.decode()


async def iterate_queue(queue: Queue[T]) -> AsyncIterable[T]:
    """Provides async iterable interface for a queue."""
    while True:
        yield await queue.get()


def import_from_string(name: str, code: str) -> ModuleType:
    """Imports module from code passed as the parameter."""
    module = ModuleType(name)
    module.__package__ = 'iftttie'
    exec(code, module.__dict__)
    return module


def cancel_all(*coros):
    for coro in coros:
        coro.cancel()


def now() -> datetime:
    return datetime.now().astimezone()


def value_tile_class(value: Any) -> str:
    if isinstance(value, bool):
        return 'is-success' if value else 'is-danger'
    return 'is-light'


def value_body_class(value: Any) -> str:
    return ''
