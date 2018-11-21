from __future__ import annotations

import json
import logging
from asyncio import CancelledError, Queue, sleep
from typing import Any

from aiohttp import ClientSession, web

from iftttie.dataclasses_ import ChannelEvent
from iftttie.sse import read_events

logger = logging.getLogger(__name__)

url = 'https://developer-api.nest.com'
headers = [('Accept', 'text/event-stream')]


async def run(app: web.Application):
    token: str = app['nest_token']
    queue: Queue[ChannelEvent] = app['event_queue']
    session: ClientSession = app['client_session']

    if not token:
        logger.warning('Nest API token is not specified.')
        return

    while True:
        try:
            logger.info('Listening to the stream…')
            async with session.get(url, params={'auth': token}, headers=headers, ssl=False) as response:
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


async def put_events(data: Any, queue: Queue[ChannelEvent]):
    for structure_id, structure in data['structures'].items():
        await queue.put(ChannelEvent(
            key=f'nest:structure:{structure_id}:away',
            value_1=(structure['away'] != 'home'),
        ))
        await queue.put(ChannelEvent(
            key=f'nest:structure:{structure_id}:wwn_security_state',
            value_1=structure['wwn_security_state'],
        ))

    devices = data['devices']
    for camera_id, camera in devices['cameras'].items():
        await queue.put(ChannelEvent(
            key=f'nest:camera:{camera_id}:is_streaming',
            value_1=camera['is_streaming'],
        ))
        await queue.put(ChannelEvent(
            key=f'nest:camera:{camera_id}:is_online',
            value_1=camera['is_online'],
        ))
    for thermostat_id, thermostat in devices['thermostats'].items():
        await queue.put(ChannelEvent(
            key=f'nest:thermostat:{thermostat_id}:ambient_temperature_c',
            value_1=thermostat['ambient_temperature_c'],
        ))
