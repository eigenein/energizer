from __future__ import annotations

import logging
from asyncio import CancelledError, Queue
from typing import Iterable

from aiohttp import web

from iftttie.dataclasses_ import Event

logger = logging.getLogger(__name__)


async def run(app: web.Application):
    queue: Queue = app['event_queue']
    while True:
        try:
            main_event: Event = await queue.get()
        except CancelledError:
            logger.info('Stopped.')
            break
        for event in propagate_event(main_event):
            logger.info(f'{event.key} {event.value_1!r} {event.value_2!r} {event.value_3!r}')
            # TODO: send to IFTTT.


def propagate_event(event: Event) -> Iterable[Event]:
    yield event
    # TODO: yield change events.
