from __future__ import annotations

from typing import AsyncIterable

from aiohttp import ClientResponse

from iftttie.dataclasses_ import ServerSideEvent


async def read_events(response: ClientResponse) -> AsyncIterable[ServerSideEvent]:
    """Read server-side events."""
    while True:
        name, values = None, []
        while True:
            line = (await response.content.readline()).rstrip(b'\n').decode()
            if not line:
                break
            key, value = line.split(':', maxsplit=1)  # type: str, str
            if value.startswith(' '):
                value = value[1:]
            if key == 'event':
                name = value
            elif key == 'data':
                values.append(value)
        yield ServerSideEvent(name=name, data='\n'.join(values))
