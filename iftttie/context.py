from __future__ import annotations

from asyncio import Task
from dataclasses import dataclass
from sqlite3 import Connection
from typing import Any, Awaitable, Callable, Iterable, Optional, Sequence, Tuple

from aiohttp import ClientSession
from loguru import logger

from iftttie.database import insert_update
from iftttie.services.base import BaseService
from iftttie.types import Update


@dataclass
class Context:
    configuration_url: str
    users: Sequence[Tuple[str, str]]
    db: Optional[Connection] = None
    session: Optional[ClientSession] = None
    run_queue_task: Optional[Task] = None
    services: Iterable[BaseService] = ()
    on_update: Callable[[Update], Awaitable[Any]] = None

    async def on_event(self, update: Update):
        """
        Handle a single event in the application context.
        """
        logger.success('{key} = {value!r}', key=update.key, value=update.value)
        insert_update(self.db, update)
        if self.on_update is not None:
            try:
                await self.on_update(update)
            except Exception as e:
                logger.opt(exception=e).error('Error while handling the event.')
