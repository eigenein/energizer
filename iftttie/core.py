from __future__ import annotations

from asyncio.queues import Queue
from asyncio.tasks import FIRST_COMPLETED, gather, sleep, wait
from concurrent.futures import CancelledError
from contextlib import suppress
from json import dumps
from typing import Any, Awaitable, Callable, Dict, Iterable, NoReturn, Optional, Tuple

import aiosqlite
from aiohttp import web
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.services.base import BaseService
from iftttie.utils import cancel_all, iterate_queue


async def run_services(app: web.Application):
    """Run services from the configuration."""
    queue: Queue[Update] = app['event_queue']

    logger.info('Running services…')
    # Get service instances from configuration.
    services: Iterable[BaseService] = getattr(app['configuration'], 'services', [])
    # We need to match a coroutine with a service to be able to restart the latter.
    coros: Dict[Any, BaseService] = {run_service(app, service): service for service in services}
    while coros:
        logger.trace('{number} coroutines pending.', number=len(coros))
        try:
            done, _ = await wait(coros.keys(), return_when=FIRST_COMPLETED)
        except CancelledError:
            cancel_all(*coros)
            return
        for coro in done:
            service: BaseService = coros[coro]
            if not coro.exception():
                yield_updates, update = coro.result()
                await queue.put(update)
                # Advance to the next update.
                coros[app.loop.create_task(async_next(yield_updates))] = service
            else:
                if not isinstance(coro.exception(), StopAsyncIteration):
                    logger.opt(exception=coro.exception()).error('{service} has failed. Restart in a minute…', service=service)
                    await sleep(60.0)
                # Spawn `yield_updates` again.
                coros[run_service(app, service)] = service
            # Coroutine is done.
            del coros[coro]
    logger.critical('No services to run.')


def run_service(app: web.Application, service: BaseService):
    logger.debug('Requesting updates from {service}…', service=service)
    return app.loop.create_task(async_next(service.yield_updates(app)))


async def async_next(coroutine: Any) -> Tuple[Any, Any]:
    # This is needed to get the original coroutine from `wait` result.
    return coroutine, await coroutine.__anext__()


async def run_queue(app: web.Application) -> NoReturn:
    """Run all the concurrent tasks."""
    logger.info('Running event queue…')
    try:
        with suppress(CancelledError):
            await gather(run_services(app), handle_updates(app), loop=app.loop)
    except Exception as e:
        logger.opt(exception=e).critical('Queue has failed.')


async def handle_updates(app: web.Application):
    """Handle updates from the queue."""
    queue: Queue[Update] = app['event_queue']
    on_update: Optional[Callable[[Update], Awaitable]] = getattr(app['configuration'], 'on_update', None)

    if on_update is None:
        logger.warning('`on_update` is not defined in the configuration.')

    with suppress(CancelledError):
        async for update in iterate_queue(queue):
            logger.success('{key} = {value!r}', key=update.key, value=update.value)
            await insert_update(app['db'], update)
            if on_update is not None:
                try:
                    await on_update(update)
                except Exception as e:
                    logger.opt(exception=e).error('Error while handling the event.')


async def insert_update(db: aiosqlite.Connection, update: Update):
    await db.execute(
        'INSERT INTO history (key, value, timestamp) VALUES (?, ?, ?)',
        (update.key, dumps(update.value), update.timestamp.timestamp()),
    )
    await db.execute(
        'INSERT OR REPLACE INTO latest (key, history_id, kind) VALUES (?, last_insert_rowid(), ?)',
        (update.key, update.kind.value),
    )
    await db.commit()
