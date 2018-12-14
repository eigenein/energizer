from __future__ import annotations

from asyncio import sleep
from typing import AsyncIterator

from aiohttp import web
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.services.base import BaseService


class Clock(BaseService):
    def __init__(self, key: str, interval: float):
        self.key = key
        self.interval = interval
        self.counter = 0

    async def yield_updates(self, app: web.Application) -> AsyncIterator[Update]:
        logger.trace('Sleeping for {interval} seconds…', interval=self.interval)
        await sleep(self.interval)
        yield Update(key=f'clock:{self.key}', value=self.counter)
        self.counter += 1

    def __str__(self) -> str:
        return f'Clock(key={self.key!r}, interval={self.interval!r})'
