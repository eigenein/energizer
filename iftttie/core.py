from __future__ import annotations

import logging
from asyncio import Queue, CancelledError

from iftttie.dataclasses_ import Event

logger = logging.getLogger(__name__)


async def handle_event_queue(queue: Queue):
    while True:
        try:
            event: Event = await queue.get()
        except CancelledError:
            logger.info('🛬 Event queue stopped.')
            break
