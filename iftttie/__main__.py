from __future__ import annotations

import ssl
from asyncio import create_task
from types import ModuleType
from typing import Optional

import click
from aiohttp import ClientSession
from loguru import logger

from iftttie import web
from iftttie.core import run_channels
from iftttie.database import init_database
from iftttie.logging_ import init_logging
from iftttie.utils import import_from_string
from iftttie.web import Context


def option(*args, **kwargs):
    return click.option(*args, show_envvar=True, **kwargs)


@click.command(context_settings={'max_content_width': 120})
@option(
    'configuration_url', '-c', '--config',
    envvar='IFTTTIE_CONFIGURATION_URL',
    required=True,
    help='Configuration URL.',
)
@option(
    'cert_path', '--cert',
    type=click.Path(exists=True, dir_okay=False),
    envvar='IFTTTIE_CERT_PATH',
    help='Server certificate path.',
)
@option(
    'key_path', '--key',
    type=click.Path(exists=True, dir_okay=False),
    envvar='IFTTTIE_KEY_PATH',
    help='Server private key path.',
)
@option(
    'verbosity', '-v', '--verbose',
    count=True,
    envvar='IFTTTIE_VERBOSITY',
    help='Logging verbosity.',
)
@option(
    'port', '-p', '--port',
    type=int,
    envvar='IFTTTIE_PORT',
    default=8443,
    show_default=True,
    help='Web interface and webhook API port.',
)
def main(
    configuration_url: str,
    cert_path: Optional[str],
    key_path: Optional[str],
    verbosity: int,
    port: int,
):
    """
    Yet another home automation service.
    """
    init_logging(verbosity)
    logger.info('Starting IFTTTie…')

    if cert_path and key_path:
        logger.info('Using SSL.')
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(cert_path, key_path)
    else:
        logger.warning('Server certificate is not specified.')
        ssl_context = None

    web.start(ssl_context, port, Context(configuration_url=configuration_url), on_startup, on_cleanup)
    logger.info('IFTTTie stopped.')


async def on_startup(app: web.Application):
    """
    Import configuration, run channels and return async tasks.
    """
    app.context.db = init_database('db.sqlite3')
    app.context.preload_latest_events()
    configuration = await import_configuration(app)
    app.context.channels = getattr(configuration, 'channels', [])
    app.context.on_event = getattr(configuration, 'on_event', None)
    app.context.on_close = getattr(configuration, 'on_close', None)
    app.context.users = getattr(configuration, 'USERS', [])
    app.context.background_task = create_task(run_channels(app))


async def import_configuration(app: web.Application) -> Optional[ModuleType]:
    """
    Download and import configuration.
    """
    logger.info('Importing configuration from {}', app.context.configuration_url)
    try:
        async with ClientSession(headers=[('Cache-Control', 'no-cache')]) as session:
            async with session.get(app.context.configuration_url) as response:
                return import_from_string('configuration', await response.text())
    except Exception as e:
        logger.error('Failed to import configuration: "{e}".', e=e)


async def on_cleanup(app: web.Application):
    """
    Cancel and close everything.
    """
    logger.info('Stopping channels…')
    app.context.background_task.cancel()
    await app.context.background_task
    logger.info('Channels stopped.')
    if app.context.on_close:
        try:
            await app.context.on_close()
        except Exception as e:
            logger.opt(exception=e).error('The error occurred in `on_close` handler.')
        else:
            logger.info('Cleaned up the configuration.')
    app.context.db.close()
    logger.info('Database is closed.')


if __name__ == '__main__':
    main()
