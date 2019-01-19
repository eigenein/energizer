from __future__ import annotations

from asyncio import Queue
from datetime import datetime
from typing import Any, Iterable, List, Tuple

from aiohttp import ClientSession
from aiohttp_sse_client.client import EventSource, MessageEvent
from loguru import logger
from multidict import MultiDict
from ujson import loads

from iftttie.dataclasses_ import Update
from iftttie.enums import Unit
from iftttie.services.base import BaseService

url = 'https://developer-api.nest.com'
headers = MultiDict([('Accept', 'text/event-stream')])
timestamp_format = '%Y-%m-%dT%H:%M:%S.%f%z'


class Nest(BaseService):
    def __init__(self, token: str):
        self.token = token

    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        while True:
            logger.debug('Listening to the stream…')
            async with EventSource(url, params={'auth': self.token}, headers=headers) as source:
                try:
                    async for event in source:
                        if event.type == 'put':
                            for update in yield_updates(event):
                                await event_queue.put(update)
                except ConnectionError as e:
                    logger.error('Connection error: {}', e)

    def __str__(self) -> str:
        return f'{Nest.__name__}(token="{self.token[:4]}…{self.token[-4:]}")'


def yield_updates(event: MessageEvent) -> Iterable[Update]:
    data: dict = loads(event.data)['data']
    devices: dict = data['devices']

    yield from yield_devices_updates(data['structures'], 'nest:structure', [
        ('away', Unit.ENUM, 'Away'),
        ('wwn_security_state', Unit.ENUM, 'Security State'),
    ])
    yield from yield_devices_updates(devices['cameras'], 'nest:camera', [
        ('is_streaming', Unit.BOOLEAN, 'Streaming'),
        ('is_online', Unit.BOOLEAN, 'Online'),
        ('snapshot_url', Unit.IMAGE_URL, 'Snapshot'),
    ])
    yield from yield_devices_updates(devices['thermostats'], 'nest:thermostat', [
        ('ambient_temperature_c', Unit.CELSIUS, 'Ambient Temperature'),
        ('humidity', Unit.RH, 'Humidity'),
        ('is_online', Unit.BOOLEAN, 'Online'),
        ('hvac_state', Unit.ENUM, 'HVAC'),
        ('target_temperature_c', Unit.CELSIUS, 'Target Temperature'),
    ])
    yield from yield_devices_updates(devices['smoke_co_alarms'], 'nest:smoke_co_alarm', [
        ('is_online', Unit.BOOLEAN, 'Online'),
    ])

    for camera_id, camera in devices['cameras'].items():
        last_event = camera.get('last_event')
        if last_event:
            yield Update(
                key=f'nest:camera:{camera_id}:last_animated_image_url',
                value=last_event['animated_image_url'],
                unit=Unit.IMAGE_URL,
                timestamp=datetime.strptime(last_event['start_time'], timestamp_format),
                title=f'{camera["name"]} Last Event',
                id_=last_event['start_time'],
            )


def yield_devices_updates(devices: dict, prefix: str, keys: List[Tuple[str, Unit, str]]) -> Iterable[Update]:
    for id_, device in devices.items():
        for key, unit, title in keys:
            yield Update(
                key=f'{prefix}:{id_}:{key}',
                value=device[key],
                unit=unit,
                title=f'{device["name"]} {title}',
            )
