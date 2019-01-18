from __future__ import annotations

from asyncio import Queue
from datetime import datetime
from typing import Any, Iterable, List, Tuple
from ujson import loads

from aiohttp import ClientSession
from aiohttp_sse_client.client import EventSource, MessageEvent
from loguru import logger
from multidict import MultiDict

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind
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
        ('away', ValueKind.ENUM),
        ('wwn_security_state', ValueKind.ENUM),
    ])
    yield from yield_devices_updates(devices['cameras'], 'nest:camera', [
        ('is_streaming', ValueKind.BOOLEAN),
        ('is_online', ValueKind.BOOLEAN),
        ('snapshot_url', ValueKind.IMAGE_URL),
    ])
    yield from yield_devices_updates(devices['thermostats'], 'nest:thermostat', [
        ('ambient_temperature_c', ValueKind.CELSIUS),
        ('humidity', ValueKind.HUMIDITY),
        ('is_online', ValueKind.BOOLEAN),
        ('hvac_state', ValueKind.ENUM),
        ('target_temperature_c', ValueKind.CELSIUS),
    ])
    yield from yield_devices_updates(devices['smoke_co_alarms'], 'nest:smoke_co_alarm', [
        ('is_online', ValueKind.BOOLEAN),
    ])

    for camera_id, camera in devices['cameras'].items():
        last_event = camera.get('last_event')
        if last_event:
            yield Update(
                key=f'nest:camera:{camera_id}:last_animated_image_url',
                value=last_event['animated_image_url'],
                kind=ValueKind.IMAGE_URL,
                timestamp=datetime.strptime(last_event['start_time'], timestamp_format),
            )


def yield_devices_updates(devices: dict, prefix: str, keys: List[Tuple[str, ValueKind]]) -> Iterable[Update]:
    for id_, device in devices.items():
        for key, kind in keys:
            yield Update(key=f'{prefix}:{id_}:{key}', value=device[key], kind=kind)
