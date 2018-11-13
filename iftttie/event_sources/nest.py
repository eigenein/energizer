from __future__ import annotations

import json
import logging
from asyncio import CancelledError, Queue
from typing import Any

from aiohttp import ClientSession, TCPConnector, web

from iftttie.dataclasses_ import Event
from iftttie.sse import read_events

logger = logging.getLogger(__name__)
url = 'https://developer-api.nest.com'
headers = [('Accept', 'text/event-stream')]


async def run(app: web.Application):
    token: str = app['nest_token']
    queue: Queue = app['event_queue']
    if not token:
        logger.warning('Nest API token is not specified.')
        return

    async with ClientSession(connector=TCPConnector(verify_ssl=False)) as session:
        while True:
            logger.info('Listening to stream…')
            try:
                async with session.get(url, params={'auth': token}, headers=headers) as response:
                    response.raise_for_status()
                    async for event in read_events(response):
                        if event.name == 'put':
                            await put_events(json.loads(event.data)['data'], queue)
                        else:
                            logger.debug(f'Ignoring event: {event.name}.')
            except CancelledError:
                logger.info('Stopped.')
                break
            except Exception as ex:
                logger.error('Error while reading stream.', exc_info=ex)


async def put_events(data: Any, queue: Queue):
    for structure_id, structure in data['structures'].items():
        await queue.put(Event(key=f'nest:structure:{structure_id}:away', value_1=(structure['away'] != 'home')))
    for camera_id, camera in data['devices']['cameras'].items():
        await queue.put(Event(key=f'nest:camera:{camera_id}:is_streaming', value_1=camera['is_streaming']))
