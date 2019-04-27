from __future__ import annotations

import asyncio
from asyncio import CancelledError, create_task, gather, sleep
from contextlib import suppress
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timedelta
from types import ModuleType
from typing import Iterable, List, Mapping

from aiohttp import ClientConnectorError, ClientSession
from loguru import logger
from sqlitemap import Connection

from my_iot.constants import ACTUAL_KEY, HTTP_TIMEOUT
from my_iot.helpers import run_in_executor, timestamp_key
from my_iot.routing import EventRouter
from my_iot.services.base import Service
from my_iot.types_ import Event

EVENT_INCLUDE = {'timestamp', 'value'}  # logged value uses optimised representation
EVENT_EXCLUDE = {'is_logged'}  # is only needed before writing


# FIXME: should be named `Runner`.
@dataclass
class Context:
    # User-defined automation.
    automation: InitVar[ModuleType]

    # Database connection.
    db: Connection

    # Event router.
    router: EventRouter = EventRouter()

    # User-defined services.
    services: Iterable[Service] = field(default_factory=list)

    # HTTP client session for user's automation needs.
    session: ClientSession = field(default_factory=lambda: ClientSession(timeout=HTTP_TIMEOUT))

    def __post_init__(self, automation: ModuleType):
        self.router = getattr(automation, 'router', None) or self.router
        self.services = getattr(automation, 'SERVICES', self.services)

    async def run_services(self):
        """
        Run all services.
        """
        logger.info('Running services…')
        try:
            await gather(*[self.run_service(service) for service in self.services])
        except CancelledError:
            for service in self.services:
                with suppress(Exception):
                    logger.info('Closing {}…', service)
                    await service.close()
        except Exception as e:
            logger.opt(exception=e).critical('Failed to run services.')

    async def run_service(self, service: Service):
        """
        Run the single service.
        """
        n_errors = 0
        while True:
            logger.info('Running {}…', service)
            try:
                async for event in service.events:
                    n_errors = 0  # the service successfully generated an event
                    await self.on_event(event)
            except CancelledError:
                logger.info('Stopped service {}.', service)
                break
            except Exception as e:
                n_errors += 1
                if isinstance(e, (ConnectionError, ClientConnectorError, asyncio.TimeoutError)):
                    logger.error('{} has raised a connection error: {}', service, e)
                else:
                    logger.opt(exception=e).error('{} has failed.', service)
            else:
                n_errors = 0  # the service has finished normally
            if n_errors:
                delay = 2.0 ** min(n_errors, 16)
                logger.error('{} errors. Restarting in {}…', n_errors, timedelta(seconds=delay))
                await sleep(delay)

    async def on_event(self, event: Event):
        """
        Handle the single event.
        """
        logger.info('{key} = {value!r}', key=event.channel, value=event.value)
        previous = self.db[ACTUAL_KEY].get(event.channel)
        await self.save_event(event)
        previous = Event(**previous) if previous is not None else None
        # noinspection PyAsyncCall
        create_task(self.router.on_event(
            event=event,
            previous=previous,
            actual=self.get_actual(),
            session=self.session,
        ))

    @run_in_executor
    def save_event(self, event: Event):
        with self.db:
            self.db[ACTUAL_KEY][event.channel] = event.dict(exclude=EVENT_EXCLUDE)
            if event.is_logged:
                self.db[f'log:{event.channel}'][timestamp_key(event.timestamp)] = event.dict(include=EVENT_INCLUDE)

    # TODO: perhaps move to `db_utils`.
    def get_actual(self) -> Mapping[str, Event]:
        """
        Get actual channel values.
        """
        return {key: Event(**value) for key, value in self.db[ACTUAL_KEY].items()}

    # TODO: perhaps move to `db_utils`.
    def get_log(self, channel: str, period: timedelta) -> List[Event]:
        """
        Gets the channel log within the specified period until now.
        """
        return [
            Event(**event)
            for event in self.db[f'log:{channel}'][timestamp_key(datetime.now() - period):]
        ]

    async def close(self):
        self.db.close()
        await self.session.close()
