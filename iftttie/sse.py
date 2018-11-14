"""Server-side events."""

from __future__ import annotations

import logging
from typing import AsyncIterable, Tuple

from aiohttp import StreamReader

from iftttie.dataclasses_ import ServerSideEvent
from iftttie.utils import read_lines

logger = logging.getLogger(__name__)


async def read_events(reader: StreamReader) -> AsyncIterable[ServerSideEvent]:
    """Read server-side events."""
    while True:
        yield await read_event(reader)


async def read_event(reader: StreamReader) -> ServerSideEvent:
    """Read single event."""
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
            logger.warning(f'Unknown key: {key}.')
    return ServerSideEvent(name=name, data='\n'.join(values))


def parse_line(line: str) -> Tuple[str, str]:
    """Parse SSE line like `data: hello`."""
    key, value = line.split(':', maxsplit=1)  # type: str, str
    if value.startswith(' '):
        value = value[1:]
    return key, value
