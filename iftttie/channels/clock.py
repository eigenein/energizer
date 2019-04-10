from __future__ import annotations

from asyncio import sleep
from datetime import timedelta
from itertools import count
from typing import Any, Optional

from loguru import logger

from iftttie.channels.base import BaseChannel
from iftttie.context import Context
from iftttie.types_ import Event


class Clock(BaseChannel):
    def __init__(self, channel_id: str, interval: timedelta, title: Optional[str] = None):
        self.channel_id = channel_id
        self.interval = interval.total_seconds()
        self.title = title

    async def run(self, context: Context, **kwargs: Any):
        for i in count(start=1):
            logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
            await sleep(self.interval)
            # FIXME: set unit.
            await context.trigger_event(Event(channel_id=f'clock:{self.channel_id}', value=i, title=self.title))

    def __str__(self) -> str:
        return f'Clock(key={self.channel_id!r}, interval={self.interval!r}, title={self.title!r})'
