from __future__ import annotations

import sys
from asyncio import FIRST_COMPLETED, CancelledError, Queue, gather, wait, sleep
from contextlib import suppress
from types import ModuleType
from typing import Any, Awaitable, Callable, Dict, Iterable, NoReturn, Optional, Tuple

import aiohttp_jinja2
import click
from aiohttp import ClientResponse, ClientSession, web
from jinja2 import PackageLoader, select_autoescape
from loguru import logger

from iftttie.constants import LOGURU_FORMAT, VERBOSITY_LEVELS
from iftttie.dataclasses_ import Update
from iftttie.exceptions import HotReloadException
from iftttie.services.base import BaseService
from iftttie.utils import import_from_string, iterate_queue, cancel_all
from iftttie.web import routes


@click.command()
@click.option('configuration_url', '-c', '--config', required=True, help='Configuration URL.')
@click.option('http_port', '--http-port', type=int, default=8080, help='Web server port.', show_default=True)
@click.option('verbosity', '-v', '--verbose', count=True, help='Logging verbosity.')
def main(configuration_url: str, http_port: int, verbosity: int):
    """Yet another home assistant."""

    logger.stop()
    logger.add(sys.stderr, format=LOGURU_FORMAT, level=VERBOSITY_LEVELS.get(verbosity, 'TRACE'))

    while True:
        logger.success('Starting IFTTTie…')
        try:
            start_web_app(http_port, configuration_url)
        except HotReloadException:
            logger.info('Hot reload requested.')
            continue  # start the app again
        else:
            break  # graceful exit
        finally:
            logger.success('IFTTTie stopped.')


def start_web_app(port: int, configuration_url: str):
    """Start the entire web app."""
    app = web.Application()
    app['configuration_url'] = configuration_url
    app['event_queue'] = Queue(maxsize=1000)  # TODO: option.
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    aiohttp_jinja2.setup(app, loader=PackageLoader('iftttie'), autoescape=select_autoescape())
    # TODO: https://aiohttp.readthedocs.io/en/stable/web_advanced.html#static-file-handling
    app.add_routes(routes)
    web.run_app(app, port=port, print=None)


async def on_startup(app: web.Application):
    """Import configuration, run services and return async tasks."""
    app['client_session'] = ClientSession(raise_for_status=True)
    app['configuration'] = await import_configuration(app)
    app[run_queue.__name__] = app.loop.create_task(run_queue(app))


async def import_configuration(app: web.Application) -> Optional[ModuleType]:
    """Download and import configuration."""
    session: ClientSession = app['client_session']
    configuration_url: str = app['configuration_url']

    logger.info(f'Importing configuration from {configuration_url}...')
    try:
        async with session.get(configuration_url, ssl=False) as response:  # type: ClientResponse
            # logger.info('ETag: {etag}.', response.headers.get('ETag'))
            return import_from_string('configuration', await response.text())
    except Exception as e:
        logger.error('Failed to import configuration: "{e}".', e=e)


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


async def on_cleanup(app: web.Application):
    """Cancel and close everything."""
    logger.info('Stopping event queue…')
    app[run_queue.__name__].cancel()
    await app[run_queue.__name__]
    await app['client_session'].close()
    logger.info('Event queue stopped.')


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
            # TODO: store it in database.
            if on_update is None:
                continue
            try:
                await on_update(update)
            except Exception as e:
                logger.opt(exception=e).error('Error while handling the event.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
