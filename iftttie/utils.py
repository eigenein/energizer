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


def update_tile_class(update: Update) -> str:
    if update.kind in (ValueKind.ON_OFF, ValueKind.YES_NO):
        return 'is-success' if update.value else 'is-danger'
    if update.kind == ValueKind.CELSIUS:
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
    if update.kind == ValueKind.HUMIDITY:
        value = update.value
        if value < 17.0:
            return 'is-link'
        if value < 34.0:
            return 'is-info'
        if value < 51.0:
            return 'is-primary'
        if value < 68.0:
            return 'is-success'
        if value < 85.0:
            return 'is-warning'
        return 'is-danger'
    if update.kind == ValueKind.BFT:
        value = update.value
        if value == 0:
            return 'is-light'
        if value == 1:
            return 'is-link'
        if value == 2:
            return 'is-info'
        if value == 3:
            return 'is-primary'
        if value == 4:
            return 'is-success'
        if value == 5:
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
    if update.kind == ValueKind.CELSIUS:
        return f'<i class="fas fa-thermometer-half"></i> {update.value}&nbsp;°C'
    if update.kind == ValueKind.HUMIDITY:
        return f'<i class="fas fa-water"></i> {update.value}%'
    if update.kind == ValueKind.IMAGE_URL:
        return f'<figure class="image"><img src="{update.value}"></figure>'
    if update.kind == ValueKind.HPA:
        return f'{update.value} hPa'
    if update.kind == ValueKind.BFT:
        return f'<i class="fas fa-wind"></i> {update.value} BFT'
    if update.kind == ValueKind.MPS:
        return f'<i class="fas fa-tachometer-alt"></i> {update.value} m/s'
    return f'<i class="far fa-question-circle"></i> {update.value}'
