from __future__ import annotations

from asyncio import Queue
from types import ModuleType
from typing import AsyncIterable, TypeVar

from aiohttp import StreamReader

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind

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


def update_tile_class(update: Update) -> str:
    if update.kind in (ValueKind.ON_OFF, ValueKind.YES_NO):
        return 'is-success' if update.value else 'is-danger'
    if update.kind == ValueKind.TEMPERATURE:
        value = update.value
        if value < 0.0:
            return 'is-link'
        if value < 10.0:
            return 'is-info'
        if value < 20.0:
            return 'is-primary'
        if value < 25.0:
            return 'is-success'
        if value < 30.0:
            return 'is-warning'
        return 'is-danger'
    return 'is-light'


def update_body_class(update: Update) -> str:
    if update.kind in (ValueKind.ON_OFF, ValueKind.YES_NO):
        return 'is-uppercase'
    return ''


def update_content(update: Update) -> str:
    if update.kind == ValueKind.ON_OFF:
        if update.value:
            return '<i class="fas fa-toggle-on"></i> <span>on</span>'
        else:
            return '<i class="fas fa-toggle-off"></i> <span>off</span>'
    if update.kind == ValueKind.YES_NO:
        if update.value:
            return '<i class="fas fa-toggle-on"></i> <span>yes</span>'
        else:
            return '<i class="fas fa-toggle-off"></i> <span>no</span>'
    if update.kind == ValueKind.TEMPERATURE:
        return f'{update.value}&nbsp;°C'
    if update.kind == ValueKind.HUMIDITY:
        return f'{update.value}%'
    return str(update.value)
