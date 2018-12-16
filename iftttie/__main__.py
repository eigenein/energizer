from __future__ import annotations

import sys
from asyncio import Queue
from types import ModuleType
from typing import Optional

import aiohttp_jinja2
import aiosqlite
import click
from aiohttp import ClientResponse, ClientSession, web
from jinja2 import PackageLoader, select_autoescape
from loguru import logger

from iftttie.constants import LOGURU_FORMAT, VERBOSITY_LEVELS, DATABASE_INIT_SCRIPT
from iftttie.core import run_queue
from iftttie.exceptions import HotReloadException
from iftttie.utils import import_from_string
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
    app['db'] = await aiosqlite.connect('db.sqlite3', loop=app.loop).__aenter__()
    await init_database(app['db'])
    app['client_session'] = await ClientSession(raise_for_status=True).__aenter__()
    app['configuration'] = await import_configuration(app)
    app[run_queue.__name__] = app.loop.create_task(run_queue(app))


async def init_database(db: aiosqlite.Connection):
    await db.executescript(DATABASE_INIT_SCRIPT)


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


async def on_cleanup(app: web.Application):
    """Cancel and close everything."""
    logger.info('Stopping event queue…')
    app[run_queue.__name__].cancel()
    await app[run_queue.__name__]
    await app['client_session'].close()
    await app['db'].close()
    logger.info('Event queue stopped.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
