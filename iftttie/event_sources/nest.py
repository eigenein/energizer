from __future__ import annotations

import json
import logging
from asyncio import CancelledError, Queue, sleep
from typing import Any, AsyncIterable

from aiohttp import ClientSession, TCPConnector, web

from iftttie.dataclasses_ import Event
from iftttie.sse import read_events

logger = logging.getLogger(__name__)
url = 'https://developer-api.nest.com'


async def run(app: web.Application):
    token: str = app['nest_token']
    queue: Queue = app['event_queue']
    if not token:
        logger.warning('Nest API token is not specified.')
        return

    async with ClientSession(
        connector=TCPConnector(verify_ssl=False),
        raise_for_status=True,
        headers=[('Accept', 'text/event-stream')],
    ) as session:
        while True:
            try:
                logger.info('Listening to stream…')
                async with session.get(url, params={'auth': token}) as response:
                    async for event in read_events(response.content):
                        if event.name == 'put':
                            await put_events(json.loads(event.data)['data'], queue)
                        else:
                            logger.debug(f'Ignoring event: {event.name}.')
            except CancelledError:
                logger.info('Stopped.')
                break
            except Exception as ex:
                logger.error('Error while reading stream.', exc_info=ex)
                await sleep(60.0)


async def put_events(data: Any, queue: Queue):
    async for event in get_events(data):
        await queue.put(event)


async def get_events(data: Any) -> AsyncIterable[Event]:
    for structure_id, structure in data['structures'].items():
        yield Event(
            key=f'nest:structure:{structure_id}:away',
            value_1=(structure['away'] != 'home'),
        )

    devices = data['devices']
    for camera_id, camera in devices['cameras'].items():
        yield Event(
            key=f'nest:camera:{camera_id}:is_streaming',
            value_1=camera['is_streaming'],
        )
    for thermostat_id, thermostat in devices['thermostats'].items():
        yield Event(
            key=f'nest:thermostat:{thermostat_id}:ambient_temperature_c',
            value_1=thermostat['ambient_temperature_c'],
        )
