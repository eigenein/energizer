from __future__ import annotations

from asyncio import sleep
from datetime import timedelta
from itertools import count
from time import time
from typing import Any, Optional

from loguru import logger

from iftttie.context import Context
from iftttie.services.base import BaseService
from iftttie.types import Update


class Clock(BaseService):
    def __init__(self, key: str, interval: timedelta, title: Optional[str] = None):
        self.key = key
        self.interval = interval.total_seconds()
        self.title = title

    async def run(self, context: Context, **kwargs: Any):
        for i in count(start=1):
            logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
            await sleep(self.interval)
            await context.on_event(Update(key=f'clock:{self.key}', value=i, title=self.title, id_=str(time())))

    def __str__(self) -> str:
        return f'Clock(key={self.key!r}, interval={self.interval!r}, title={self.title!r})'
