from __future__ import annotations

from asyncio import sleep
from datetime import timedelta
from pathlib import Path
from typing import Any, Optional

from loguru import logger

from iftttie.channels.base import BaseChannel
from iftttie.context import Context
from iftttie.types_ import Event, Unit


class File(BaseChannel):
    def __init__(self, path: Path, key: str, interval: timedelta, unit: Unit, title: Optional[str] = None):
        self.path = path
        self.key = key
        self.interval = interval.total_seconds()
        self.unit = unit
        self.title = title

    async def run(self, context: Context, **kwargs: Any):
        while True:
            try:
                await context.trigger_event(Event(
                    key=f'file:{self.key}',
                    value=self.preprocess_value(self.path.read_text()),
                    unit=self.unit,
                    title=self.title,
                ))
            except IOError as e:
                logger.error('I/O error in {channel}:', channel=self)
                logger.error('{e}', e=e)
            logger.debug('Next reading in {interval} seconds.', interval=self.interval)
            await sleep(self.interval)

    def preprocess_value(self, value: str) -> Any:
        return value

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(path={self.path!r}, title={self.title!r})'


class FloatValueFile(File):
    def __init__(self, path: Path, key: str, interval: timedelta, unit: Unit, scale=1.0, title: Optional[str] = None):
        super().__init__(path, key, interval, unit, title)
        self.scale = scale

    def preprocess_value(self, value: str):
        return float(value.strip()) * self.scale
