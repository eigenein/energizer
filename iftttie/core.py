from __future__ import annotations

from asyncio.tasks import gather, sleep
from concurrent.futures import CancelledError
from contextlib import suppress
from typing import Awaitable, Callable, Iterable, NoReturn, Optional

from aiohttp import ClientConnectorError
from loguru import logger

from iftttie import web
from iftttie.database import insert_update
from iftttie.services.base import BaseService
from iftttie.types import Update
from iftttie.utils import iterate_queue


async def run_services(app: web.Application):
    """Run services from the configuration."""

    logger.info('Running services…')
    services: Iterable[BaseService] = getattr(app.context.configuration, 'services', [])
    if services:
        await gather(*(run_service(app, service) for service in services))
    else:
        logger.critical('No services to run.')


async def run_service(app: web.Application, service: BaseService):
    while True:
        logger.info('Running {service}…', service=service)
        try:
            await service.run(app.context.session, app.context.event_queue, app=app)
        except CancelledError:
            logger.debug('Stopped service {service}.', service=service)
            break
        except ClientConnectorError as e:
            logger.error('{service} has raised a connection error:', service=service)
            logger.error('{e}', e=e)
        except Exception as e:
            logger.opt(exception=e).error('{service} has failed.', service=service)
        logger.error('Restarting in a minute.')
        await sleep(60.0)


async def run_queue(app: web.Application) -> NoReturn:
    """Run all the concurrent tasks."""
    logger.info('Running event queue…')
    with suppress(CancelledError):
        await gather(run_services(app), handle_updates(app), loop=app.loop)


async def handle_updates(app: web.Application):
    """Handle updates from the queue."""
    on_update: Optional[Callable[[Update], Awaitable]] = getattr(app.context.configuration, 'on_update', None)

    if on_update is None:
        logger.warning('`on_update` is not defined in the configuration.')

    async for update in iterate_queue(app.context.event_queue):
        logger.success('{key} = {value!r}', key=update.key, value=update.value)
        insert_update(app.context.db, update)
        if on_update is None:
            continue
        try:
            await on_update(update)
        except Exception as e:
            logger.opt(exception=e).error('Error while handling the event.')
