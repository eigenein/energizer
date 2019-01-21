from __future__ import annotations

from asyncio import Task
from dataclasses import dataclass
from sqlite3 import Connection
from typing import Any, Awaitable, Callable, Iterable, Optional, Sequence, Tuple

from aiohttp import ClientSession
from loguru import logger

from iftttie.channels.base import BaseChannel
from iftttie.database import insert_event
from iftttie.types import Event


@dataclass
class Context:
    configuration_url: str
    users: Sequence[Tuple[str, str]]
    db: Optional[Connection] = None
    session: Optional[ClientSession] = None
    run_channels_task: Optional[Task] = None
    channels: Iterable[BaseChannel] = ()
    on_event: Callable[[Event], Awaitable[Any]] = None

    async def trigger_event(self, event: Event):
        """
        Handle a single event in the application context.
        """
        logger.success('{key} = {value!r}', key=event.key, value=event.value)
        insert_event(self.db, event)
        if self.on_event is not None:
            try:
                await self.on_event(event)
            except Exception as e:
                logger.opt(exception=e).error('Error while handling the event.')
