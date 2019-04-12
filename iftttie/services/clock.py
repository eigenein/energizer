from __future__ import annotations

from asyncio import sleep
from datetime import timedelta
from itertools import count
from typing import Optional

from loguru import logger

from iftttie.services.base import Service
from iftttie.types_ import Event


class Clock(Service):
    def __init__(self, channel_id: str, interval: timedelta, title: Optional[str] = None):
        self.channel_id = channel_id
        self.interval = interval.total_seconds()
        self.title = title

    @property
    async def events(self):
        for i in count(start=1):
            logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
            await sleep(self.interval)
            # FIXME: set unit.
            yield Event(channel_id=f'clock:{self.channel_id}', value=i, title=self.title)

    def __str__(self) -> str:
        return f'Clock(key={self.channel_id!r}, interval={self.interval!r}, title={self.title!r})'
