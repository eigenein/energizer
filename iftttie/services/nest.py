from __future__ import annotations

import json
import logging
from asyncio import Queue
from typing import Any

from aiohttp import ClientSession, web

from iftttie.dataclasses_ import ChannelEvent
from iftttie.services.base import Base
from iftttie.sse import read_events

logger = logging.getLogger(__name__)

url = 'https://developer-api.nest.com'
headers = [('Accept', 'text/event-stream')]


class Nest(Base):
    def __init__(self, token: str):
        self.token = token

    async def run(self, app: web.Application):
        queue: Queue[ChannelEvent] = app['event_queue']
        session: ClientSession = app['client_session']

        logger.info('Listening to the stream…')
        async with session.get(url, params={'auth': self.token}, headers=headers, ssl=False) as response:
            async for event in read_events(response.content):
                if event.name == 'put':
                    await put_events(json.loads(event.data)['data'], queue)
                else:
                    logger.debug(f'Ignoring event: {event.name}.')


async def put_events(data: Any, queue: Queue[ChannelEvent]):
    for structure_id, structure in data['structures'].items():
        await queue.put(ChannelEvent(
            key=f'nest:structure:{structure_id}:away',
            value=structure['away'],
        ))
        await queue.put(ChannelEvent(
            key=f'nest:structure:{structure_id}:wwn_security_state',
            value=structure['wwn_security_state'],
        ))

    devices = data['devices']
    for camera_id, camera in devices['cameras'].items():
        await queue.put(ChannelEvent(
            key=f'nest:camera:{camera_id}:is_streaming',
            value=camera['is_streaming'],
        ))
        await queue.put(ChannelEvent(
            key=f'nest:camera:{camera_id}:is_online',
            value=camera['is_online'],
        ))
    for thermostat_id, thermostat in devices['thermostats'].items():
        await queue.put(ChannelEvent(
            key=f'nest:thermostat:{thermostat_id}:ambient_temperature_c',
            value=thermostat['ambient_temperature_c'],
        ))
