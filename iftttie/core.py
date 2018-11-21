from __future__ import annotations

import logging
from asyncio import CancelledError, gather, Queue
from contextlib import suppress

from aiohttp import ClientSession, web

from iftttie.channels import nest
from iftttie.dataclasses_ import ChannelEvent
from iftttie.utils import iterate_queue

logger = logging.getLogger(__name__)

channels = (
    nest.run,
)


async def start_queue(app: web.Application):
    logger.info('Starting event queue…')
    app['client_session'] = ClientSession(loop=app.loop, raise_for_status=True)
    app['process_queue'] = app.loop.create_task(process_queue(app))


async def stop_queue(app: web.Application):
    logger.info('Stopping event queue…')
    app['process_queue'].cancel()
    await app['process_queue']
    await app['client_session'].close()
    logger.info('Event queue stopped.')


async def process_queue(app: web.Application):
    with suppress(CancelledError):
        await gather(handle_events(app), *(channel(app) for channel in channels), loop=app.loop)


async def handle_events(app: web.Application):
    queue: Queue[ChannelEvent] = app['event_queue']
    with suppress(CancelledError):
        async for event in iterate_queue(queue):
            logger.info(f'{event.key} {event.value_1!r} {event.value_2!r} {event.value_3!r}')
