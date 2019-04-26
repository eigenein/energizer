from __future__ import annotations

from asyncio import sleep
from datetime import timedelta
from itertools import count
from typing import Optional

from loguru import logger

from my_iot.services.base import Service
from my_iot.types_ import Event, Unit


class Clock(Service):
    def __init__(self, sub_channel: str, interval: timedelta, title: Optional[str] = None):
        self.sub_channel = sub_channel
        self.interval = interval.total_seconds()
        self.title = title

    @property
    async def events(self):
        for i in count(start=1):
            logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
            await sleep(self.interval)
            yield Event(channel=f'clock:{self.sub_channel}', value=i, title=self.title, unit=Unit.TEXT)

    def __str__(self) -> str:
        return f'Clock(key={self.sub_channel!r}, interval={self.interval!r}, title={self.title!r})'
