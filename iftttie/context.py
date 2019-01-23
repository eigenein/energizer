from __future__ import annotations

from asyncio import Task
from dataclasses import dataclass, field
from sqlite3 import Connection
from typing import Any, Awaitable, Callable, Iterable, Optional, Sequence, Tuple, Dict

from aiohttp import ClientSession
from loguru import logger

from iftttie.channels.base import BaseChannel
from iftttie.database import insert_event, select_latest
from iftttie.types import Event


@dataclass
class Context:
    # Configuration URL passed via the command line option.
    configuration_url: str

    # Users credentials, each item is a `(username, password_hash)` pair.
    # See also `iftttie.utils password-hash`.
    users: Sequence[Tuple[str, str]] = field(default_factory=list)

    # Database connection.
    db: Optional[Connection] = None

    # Client session used in channels.
    session: Optional[ClientSession] = None

    # `asyncio` task for the channels.
    run_channels_task: Optional[Task] = None

    # Channel instances.
    channels: Iterable[BaseChannel] = ()

    # User's event handler.
    on_event: Callable[..., Awaitable[Any]] = None

    # Latest events cache.
    latest_events: Dict[str, Event] = field(default_factory=dict)

    def preload_latest_events(self):
        logger.info('Pre-loading latest events…')
        self.latest_events = {event.key: event for event in select_latest(self.db)}

    async def trigger_event(self, event: Event):
        """
        Handle a single event in the application context.
        """
        logger.success('{key} = {value!r}', key=event.key, value=event.value)
        old_event = self.latest_events.get(event.key)  # for the faster access to the previous value
        insert_event(self.db, event)
        self.latest_events[event.key] = event  # for the faster access by key in the user code
        if self.on_event is None:
            return
        try:
            await self.on_event(
                event=event,
                old_event=old_event,
                latest_events=self.latest_events,
                session=self.session,
            )
        except Exception as e:
            logger.opt(exception=e).error('Error while handling the event.')
