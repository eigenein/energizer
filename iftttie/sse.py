"""Server-side events."""

from __future__ import annotations

from typing import AsyncIterable, Tuple

from aiohttp import StreamReader
from loguru import logger

from iftttie.dataclasses_ import ServerSideEvent
from iftttie.utils import read_lines


async def read_events(reader: StreamReader) -> AsyncIterable[ServerSideEvent]:
    """Read server-side events as an iterable."""
    while not reader.at_eof():
        yield await read_event(reader)
    logger.debug('Event stream has ended.')


async def read_event(reader: StreamReader) -> ServerSideEvent:
    """Read a single server-side event."""
    name, values = None, []
    async for line in read_lines(reader):
        line = line.rstrip('\n')
        if not line:
            break
        key, value = parse_line(line)
        if key == 'event':
            name = value
        elif key == 'data':
            values.append(value)
        else:
            logger.warning('Unknown key: {key}.', key=key)
    logger.trace('Event: {name}.', name=name)
    return ServerSideEvent(name=name, data='\n'.join(values))


def parse_line(line: str) -> Tuple[str, str]:
    """Parse server-side event line like `data: hello`."""
    key, value = line.split(':', maxsplit=1)  # type: str, str
    if value.startswith(' '):
        value = value[1:]
    return key, value
