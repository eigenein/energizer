from __future__ import annotations

import logging
from asyncio import CancelledError
from typing import Iterable

from aiohttp import web

from iftttie.dataclasses_ import Event
from iftttie.utils import iterate_queue

logger = logging.getLogger(__name__)


async def run(app: web.Application):
    try:
        async for main_event in iterate_queue(app['event_queue']):
            for event in propagate_event(main_event):
                logger.info(f'{event.key} {event.value_1!r} {event.value_2!r} {event.value_3!r}')
                # TODO: send to IFTTT.
    except CancelledError:
        logger.info('Stopped.')


def propagate_event(event: Event) -> Iterable[Event]:
    yield event
    # TODO: yield change events.
