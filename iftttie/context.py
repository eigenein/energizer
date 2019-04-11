from __future__ import annotations

from asyncio import Task, create_task
from dataclasses import InitVar, dataclass, field
from datetime import timezone
from typing import Any, Awaitable, Callable, Mapping, Optional, Sequence, Tuple

from loguru import logger
from sqlitemap import Connection

from iftttie.constants import ACTUAL_KEY
from iftttie.types_ import Event

utc = timezone.utc


@dataclass
class Context:
    # Setup module.
    setup: InitVar[Any]

    # Database connection.
    db: Connection

    # Users credentials, each item is a `(username, password_hash)` pair.
    # See also `iftttie.utils password-hash`.
    users: Sequence[Tuple[str, str]] = field(default_factory=list)

    # `asyncio` task for the channels.
    background_task: Optional[Task] = None

    # User's event handler.
    on_event: Callable[..., Awaitable[Any]] = None

    # User's clean up handler.
    # TODO: rename.
    on_close: Callable[[], Awaitable[Any]] = None

    def __post_init__(self, setup: Any):
        self.channels = getattr(setup, 'channels', [])  # TODO: should be auto-discovered.
        self.on_event = getattr(setup, 'on_event', None)  # TODO: should be set by a user code.
        self.on_close = getattr(setup, 'on_close', None)  # TODO: should be set by a user code.
        self.users = getattr(setup, 'USERS', [])  # TODO: should be set by a user code.

    def get_actual(self) -> Mapping[str, Event]:
        """
        Get actual sensor values.
        """
        return {key: Event(**value) for key, value in self.db[ACTUAL_KEY].items()}

    async def trigger_event(self, event: Event):
        """
        Handle a single event in the application context.
        """
        logger.info('{key} = {value!r}', key=event.channel_id, value=event.value)
        previous = self.db[ACTUAL_KEY].get(event.channel_id)
        with self.db:
            self.db[ACTUAL_KEY][event.channel_id] = event.dict()
            if event.is_logged:
                # Historical value uses optimised representation.
                self.db[f'log:{event.channel_id}'][event.key] = event.dict(include={'timestamp', 'value'})
        if self.on_event is not None:
            previous = Event(**previous) if previous is not None else None
            await create_task(self.call_event_handler(event, previous))

    async def call_event_handler(self, event: Event, previous: Optional[Event]):
        # This has to stay in a separate function to be able to catch errors.
        try:
            await self.on_event(event=event, previous=previous, actual=self.get_actual())
        except Exception as e:
            logger.opt(exception=e).error('Error while handling the event.')
