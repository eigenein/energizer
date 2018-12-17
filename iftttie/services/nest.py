from __future__ import annotations

import json
from asyncio import Queue
from datetime import datetime
from typing import Any, Iterable

from aiohttp import ClientSession
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind
from iftttie.services.base import BaseService
from iftttie.sse import read_events

url = 'https://developer-api.nest.com'
headers = [('Accept', 'text/event-stream')]
timestamp_format = '%Y-%m-%dT%H:%M:%S.%fZ'


class Nest(BaseService):
    def __init__(self, token: str):
        self.token = token

    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        logger.debug('Listening to the stream…')
        async with client_session.get(url, params={'auth': self.token}, headers=headers, timeout=None) as response:
            async for event in read_events(response.content):
                if event.name != 'put':
                    logger.debug('Ignoring event: {name}.', name=event.name)
                    continue
                for update in yield_updates(json.loads(event.data)['data']):
                    await event_queue.put(update)

    def __str__(self) -> str:
        return f'{Nest.__name__}(token="{self.token[:4]}…{self.token[-4:]}")'


def yield_updates(data: Any) -> Iterable[Update]:
    for structure_id, structure in data['structures'].items():
        yield Update(key=f'nest:structure:{structure_id}:away', value=structure['away'])
        yield Update(key=f'nest:structure:{structure_id}:wwn_security_state', value=structure['wwn_security_state'])

    devices = data['devices']
    for camera_id, camera in devices['cameras'].items():
        yield Update(key=f'nest:camera:{camera_id}:is_streaming', value=camera['is_streaming'], kind=ValueKind.ON_OFF)
        yield Update(key=f'nest:camera:{camera_id}:is_online', value=camera['is_online'], kind=ValueKind.YES_NO)
        last_event = camera.get('last_event')
        if last_event:
            yield Update(
                key=f'nest:camera:{camera_id}:last_animated_image_url',
                value=last_event['animated_image_url'],
                kind=ValueKind.IMAGE_URL,
                timestamp=datetime.strptime(last_event['start_time'], timestamp_format).astimezone(),
            )
    for thermostat_id, thermostat in devices['thermostats'].items():
        yield Update(
            key=f'nest:thermostat:{thermostat_id}:ambient_temperature_c',
            value=thermostat['ambient_temperature_c'],
            kind=ValueKind.CELSIUS,
        )
        yield Update(
            key=f'nest:thermostat:{thermostat_id}:humidity',
            value=thermostat['humidity'],
            kind=ValueKind.HUMIDITY,
        )
        yield Update(
            key=f'nest:thermostat:{thermostat_id}:is_online',
            value=thermostat['is_online'],
            kind=ValueKind.YES_NO,
        )
