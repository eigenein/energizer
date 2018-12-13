from __future__ import annotations

import json
from asyncio import Queue
from typing import Any

from aiohttp import ClientSession, web
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.services.base import BaseService
from iftttie.sse import read_events

url = 'https://developer-api.nest.com'
headers = [('Accept', 'text/event-stream')]


class Nest(BaseService):
    def __init__(self, token: str):
        self.token = token

    async def run(self, app: web.Application):
        queue: Queue[Update] = app['event_queue']
        session: ClientSession = app['client_session']

        logger.debug('Listening to the stream…')
        async with session.get(url, params={'auth': self.token}, headers=headers, ssl=False) as response:
            async for event in read_events(response.content):
                if event.name == 'put':
                    await put_updates(json.loads(event.data)['data'], queue)
                else:
                    logger.debug('Ignoring event: {name}.', name=event.name)

    def __str__(self) -> str:
        return Nest.__name__


async def put_updates(data: Any, queue: Queue[Update]):
    for structure_id, structure in data['structures'].items():
        await queue.put(Update(
            key=f'nest:structure:{structure_id}:away',
            value=structure['away'],
        ))
        await queue.put(Update(
            key=f'nest:structure:{structure_id}:wwn_security_state',
            value=structure['wwn_security_state'],
        ))

    devices = data['devices']
    for camera_id, camera in devices['cameras'].items():
        await queue.put(Update(
            key=f'nest:camera:{camera_id}:is_streaming',
            value=camera['is_streaming'],
        ))
        await queue.put(Update(
            key=f'nest:camera:{camera_id}:is_online',
            value=camera['is_online'],
        ))
    for thermostat_id, thermostat in devices['thermostats'].items():
        await queue.put(Update(
            key=f'nest:thermostat:{thermostat_id}:ambient_temperature_c',
            value=thermostat['ambient_temperature_c'],
        ))
