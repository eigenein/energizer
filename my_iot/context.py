from __future__ import annotations

from asyncio import create_task
from dataclasses import InitVar, dataclass, field
from types import ModuleType
from typing import Iterable, List, Mapping, Tuple

from aiohttp import ClientSession
from loguru import logger
from sqlitemap import Connection

from my_iot.constants import ACTUAL_KEY, HTTP_TIMEOUT
from my_iot.routing import EventRouter
from my_iot.services.base import Service
from my_iot.types_ import Event


@dataclass
class Context:
    # User-defined automation.
    automation: InitVar[ModuleType]

    # Database connection.
    db: Connection

    # User names and password hashes.
    users: List[Tuple[str, str]] = field(default_factory=list)

    # Event router.
    router: EventRouter = EventRouter()

    # User-defined services.
    services: Iterable[Service] = field(default_factory=list)

    # HTTP client session available for user.
    session: ClientSession = field(default_factory=lambda: ClientSession(timeout=HTTP_TIMEOUT))

    def __post_init__(self, automation: ModuleType):
        self.users = getattr(automation, 'USERS', self.users)
        self.router = getattr(automation, 'router', None) or self.router
        self.services = getattr(automation, 'SERVICES', self.services)

    def get_actual(self) -> Mapping[str, Event]:
        """
        Get actual sensor values.
        """
        return {key: Event(**value) for key, value in self.db[ACTUAL_KEY].items()}

    def trigger_event(self, event: Event):
        """
        Handle a single event in the application context.
        """
        logger.info('{key} = {value!r}', key=event.channel, value=event.value)
        previous = self.db[ACTUAL_KEY].get(event.channel)

        with self.db:
            self.db[ACTUAL_KEY][event.channel] = event.dict(exclude={'is_logged'})
            if event.is_logged:
                # Historical value uses optimised representation.
                self.db[f'log:{event.channel}'][event.key] = event.dict(include={'timestamp', 'value'})

        previous = Event(**previous) if previous is not None else None
        # noinspection PyAsyncCall
        create_task(self.router.on_event(
            event=event,
            previous=previous,
            actual=self.get_actual(),
            session=self.session,
        ))

    async def close(self):
        self.db.close()
        await self.session.close()
