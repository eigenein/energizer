from __future__ import annotations

from asyncio import Queue, sleep
from datetime import timedelta
from typing import Any

from aiohttp import ClientSession
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.services.base import BaseService


class Clock(BaseService):
    def __init__(self, key: str, interval: timedelta):
        self.key = key
        self.interval = interval.total_seconds()

    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        counter = 0

        while True:
            logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
            await sleep(self.interval)
            await event_queue.put(Update(key=f'clock:{self.key}', value=counter))
            counter += 1

    def __str__(self) -> str:
        return f'Clock(key={self.key!r}, interval={self.interval!r})'
