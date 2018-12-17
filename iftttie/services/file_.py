from __future__ import annotations

from asyncio import sleep
from asyncio.queues import Queue
from datetime import timedelta
from pathlib import Path
from typing import Any

from aiohttp import ClientSession
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind
from iftttie.services.base import BaseService


class File(BaseService):
    def __init__(self, path: Path, key: str, interval: timedelta, kind: ValueKind):
        self.path = path
        self.key = key
        self.interval = interval.total_seconds()
        self.kind = kind

    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        while True:
            try:
                await event_queue.put(Update(
                    key=f'file:{self.key}',
                    value=self.preprocess_value(self.path.read_text()),
                    kind=self.kind,
                ))
            except IOError as e:
                logger.error('I/O error in {service}:', service=self)
                logger.error('{e}', e=e)
            logger.debug('Next reading in {interval} seconds.', interval=self.interval)
            await sleep(self.interval)

    def preprocess_value(self, value: str) -> Any:
        return value

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(path={self.path!r})'


class FloatFile(File):
    def __init__(self, path: Path, key: str, interval: timedelta, kind: ValueKind, scale=1.0):
        super().__init__(path, key, interval, kind)
        self.scale = scale

    def preprocess_value(self, value: str):
        return float(value.strip()) * self.scale
