from __future__ import annotations

from asyncio import Task, create_task
from dataclasses import dataclass, field
from datetime import timezone
from types import ModuleType
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence, Tuple

from loguru import logger
from sqlitemap import Connection

from iftttie.constants import ACTUAL_KEY
from iftttie.types_ import Event

utc = timezone.utc


@dataclass
class Context:
    # Setup module.
    # TODO: this should be an init-only parameter.
    setup: Optional[ModuleType] = None

    # Users credentials, each item is a `(username, password_hash)` pair.
    # See also `iftttie.utils password-hash`.
    users: Sequence[Tuple[str, str]] = field(default_factory=list)

    # Database connection.
    db: Connection = None

    # `asyncio` task for the channels.
    background_task: Optional[Task] = None

    # User's event handler.
    on_event: Callable[..., Awaitable[Any]] = None

    # User's clean up handler.
    # TODO: rename.
    on_close: Callable[[], Awaitable[Any]] = None

    @property
    def actual(self) -> Mapping[str, Event]:
        """
        Get actual sensor values.
        """
        return {key: Event(**value) for key, value in self.db[ACTUAL_KEY].items()}

    async def trigger_event(self, event: Event):
        """
        Handle a single event in the application context.
        """
        logger.info('{key} = {value!r}', key=event.key, value=event.value)
        with self.db:
            # Historical value uses optimised representation.
            self.db[f'log:{event.key}'][event.db_key] = event.dict(include={'timestamp', 'value'})
            self.db[ACTUAL_KEY][event.key] = event.dict()
        if self.on_event is not None:
            await create_task(self.call_event_handler(event))

    async def call_event_handler(self, event: Event):
        # This has to stay in a separate function to be able to catch errors.
        try:
            await self.on_event(event=event, actual=self.actual)
        except Exception as e:
            logger.opt(exception=e).error('Error while handling the event.')
