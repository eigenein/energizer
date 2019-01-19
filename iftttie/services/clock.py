from __future__ import annotations

from asyncio import Queue, sleep
from datetime import timedelta
from itertools import count
from typing import Any, Optional

from aiohttp import ClientSession
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.services.base import BaseService


class Clock(BaseService):
    def __init__(self, key: str, interval: timedelta, title: Optional[str] = None):
        self.key = key
        self.interval = interval.total_seconds()
        self.title = title

    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        for i in count():
            logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
            await sleep(self.interval)
            await event_queue.put(Update(key=f'clock:{self.key}', value=i, title=self.title))

    def __str__(self) -> str:
        return f'Clock(key={self.key!r}, interval={self.interval!r})'
