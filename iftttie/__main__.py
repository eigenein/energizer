from __future__ import annotations

import sys
from asyncio import CancelledError, Queue, gather
from contextlib import suppress
from types import ModuleType
from typing import Awaitable, Callable, Iterable, Optional

import aiohttp_jinja2
import click
from aiohttp import ClientResponse, ClientSession, web
from jinja2 import PackageLoader, select_autoescape
from loguru import logger

from iftttie.constants import LOGURU_FORMAT, VERBOSITY_LEVELS
from iftttie.dataclasses_ import Update
from iftttie.exceptions import HotReloadException
from iftttie.services.base import BaseService
from iftttie.utils import import_from_string, iterate_queue
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
        logger.info('Starting IFTTTie…')
        try:
            start_web_app(http_port, configuration_url)
        except HotReloadException:
            logger.info('Hot reload requested.')
            continue  # start the app again
        else:
            break  # graceful exit
        finally:
            logger.info('IFTTTie stopped.')


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
    await import_configuration(app)
    app[run_queue.__name__] = app.loop.create_task(run_queue(app, *run_services(app)))


async def import_configuration(app: web.Application) -> Optional[ModuleType]:
    """Download and import configuration."""
    session: ClientSession = app['client_session']
    configuration_url: str = app['configuration_url']

    logger.info(f'Importing configuration from {configuration_url}...')
    try:
        async with session.get(configuration_url, ssl=False) as response:  # type: ClientResponse
            app['configuration'] = import_from_string('configuration', await response.text())
    except Exception as e:
        logger.error(f'Failed to import configuration: "{e}". No services will be run.')


def run_services(app: web.Application) -> Iterable[Awaitable]:
    """Discover and run services in the configuration."""
    logger.info('Discovering and running services…')
    configuration: ModuleType = app['configuration']
    for name in dir(configuration):
        if name.startswith('_'):
            continue
        value = getattr(configuration, name)
        if isinstance(value, BaseService):
            logger.info(f'Running {name}…')
            yield value.run(app)


async def on_cleanup(app: web.Application):
    """Cancel and close everything."""
    logger.info('Stopping event queue…')
    app[run_queue.__name__].cancel()
    await app[run_queue.__name__]
    await app['client_session'].close()
    logger.info('Event queue stopped.')


async def run_queue(app: web.Application, *tasks: Awaitable):
    """Run all the concurrent tasks."""
    logger.info('Running event queue…')
    with suppress(CancelledError):
        # FIXME: handle errors from the tasks and restart them. Perhaps with `wait`.
        await gather(handle_updates(app), *tasks, loop=app.loop, return_exceptions=True)


async def handle_updates(app: web.Application):
    """Handle updates from the queue."""
    queue: Queue[Update] = app['event_queue']
    on_update: Optional[Callable[[Update], Awaitable]] = getattr(app['configuration'], 'on_update', None)

    if on_update is None:
        logger.warning('`on_update` is not defined in the configuration.')

    with suppress(CancelledError):
        async for update in iterate_queue(queue):
            logger.success(f'{update.key}({update.value!r})')
            # TODO: store it in database.
            if on_update is None:
                continue
            try:
                await on_update(update)
            except Exception as e:
                logger.error('Error while handling the event.', exc_info=e)


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
