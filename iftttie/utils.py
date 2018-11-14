from __future__ import annotations

import logging
from asyncio import Queue
from typing import AsyncIterable

import click
from aiohttp import StreamReader


def setup_logging():
    logging.basicConfig(
        format='%(asctime)s [%(levelname).1s] (%(name)s) %(message)s',
        stream=click.get_text_stream('stderr'),
        datefmt='%b %d %H:%M:%S',
        level=logging.DEBUG,
    )


async def read_lines(reader: StreamReader) -> AsyncIterable[str]:
    while True:
        line: bytes = await reader.readline()
        if not line:
            break
        yield line.decode()


async def iterate_queue(queue: Queue) -> AsyncIterable:
    while True:
        yield await queue.get()
