from __future__ import annotations

import ssl
from asyncio import Queue
from types import ModuleType
from typing import Optional

import aiohttp_jinja2
import aiosqlite
import click
from aiohttp import ClientSession, web
from jinja2 import PackageLoader, select_autoescape
from loguru import logger

from iftttie.core import run_queue
from iftttie.database import init_database
from iftttie.enums import Unit
from iftttie.logging_ import init_logging
from iftttie.utils import import_from_string
from iftttie.web import routes


@click.command(context_settings={'max_content_width': 120})
@click.option(
    'configuration_url', '-c', '--config',
    envvar='IFTTTIE_CONFIGURATION_URL',
    show_envvar=True,
    required=True,
    help='Configuration URL.',
)
@click.option(
    'cert_path', '--cert',
    type=click.Path(exists=True, dir_okay=False),
    envvar='IFTTTIE_CERT_PATH',
    show_envvar=True,
    help='Server certificate path.',
)
@click.option(
    'key_path', '--key',
    type=click.Path(exists=True, dir_okay=False),
    envvar='IFTTTIE_KEY_PATH',
    show_envvar=True,
    help='Server private key path.',
)
@click.option(
    'verbosity', '-v', '--verbose',
    count=True,
    envvar='IFTTTIE_VERBOSITY',
    show_envvar=True,
    help='Logging verbosity.',
)
def main(configuration_url: str, cert_path: Optional[str], key_path: Optional[str], verbosity: int):
    """
    Yet another home automation service.
    """
    init_logging(verbosity)
    logger.success('Starting IFTTTie…')

    if cert_path and key_path:
        logger.success('Using SSL.')
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(cert_path, key_path)
    else:
        logger.warning('Server certificate is not specified.')
        ssl_context = None

    start_web_app(ssl_context, configuration_url)
    logger.success('IFTTTie stopped.')


def start_web_app(ssl_context: Optional[ssl.SSLContext], configuration_url: str):
    """Start the entire web app."""
    app = web.Application()

    app['configuration_url'] = configuration_url
    app['event_queue'] = Queue(maxsize=1000)  # TODO: option.

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    env = aiohttp_jinja2.setup(app, loader=PackageLoader('iftttie'), autoescape=select_autoescape())
    env.globals['Unit'] = Unit
    env.filters['datetime'] = '{:%b %d %H:%M:%S}'.format

    app.add_routes(routes)
    web.run_app(app, port=8443, ssl_context=ssl_context, print=None)


async def on_startup(app: web.Application):
    """Import configuration, run services and return async tasks."""
    app['db'] = await aiosqlite.connect('db.sqlite3', loop=app.loop).__aenter__()
    await init_database(app['db'])
    app['client_session'] = await ClientSession(raise_for_status=True).__aenter__()
    app['configuration'] = await import_configuration(app)
    app['display_names'] = getattr(app['configuration'], 'display_names', {})
    app[run_queue.__name__] = app.loop.create_task(run_queue(app))


async def import_configuration(app: web.Application) -> Optional[ModuleType]:
    """Download and import configuration."""
    session: ClientSession = app['client_session']
    configuration_url: str = app['configuration_url']

    logger.info(f'Importing configuration from {configuration_url}...')
    try:
        async with session.get(configuration_url, headers=[('Cache-Control', 'no-cache')]) as response:
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
