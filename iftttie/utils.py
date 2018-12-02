from __future__ import annotations

import logging
from asyncio import Queue
from types import ModuleType
from typing import AsyncIterable, TypeVar, Dict, Any

import click
from aiohttp import StreamReader

T = TypeVar('T')


def setup_logging(verbosity: int):
    if verbosity == 0:
        level = logging.ERROR
    elif verbosity == 1:
        level = logging.WARNING
    elif verbosity == 2:
        level = logging.INFO
    else:
        level = logging.DEBUG

    logging.basicConfig(
        format='%(asctime)s [%(levelname).1s] (%(name)s) %(message)s',
        stream=click.get_text_stream('stderr'),
        datefmt='%b %d %H:%M:%S',
        level=level,
    )


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
