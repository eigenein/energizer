from __future__ import annotations

import ssl
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
@click.option(
    'port', '-p', '--port',
    type=int,
    envvar='IFTTTIE_PORT',
    show_envvar=True,
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
    """Import configuration, run channels and return async tasks."""
    app.context.db = init_database('db.sqlite3')
    app.context.preload_latest_events()
    configuration = await import_configuration(app)

    app.context.channels = getattr(configuration, 'channels', [])
    if app.context.channels:
        logger.info('{} channels are defined', len(app.context.channels))
    else:
        logger.error('No channels to run.')

    app.context.on_event = getattr(configuration, 'on_event', None)
    if app.context.on_event:
        logger.info('`on_event` is defined.')
    else:
        logger.warning('`on_event` is not defined in the configuration.')

    app.context.on_close = getattr(configuration, 'on_close', None)
    if app.context.on_close:
        logger.info('`on_close` is defined.')
    else:
        logger.warning('`on_close` is not defined in the configuration.')

    app.context.users = getattr(configuration, 'USERS', [])
    if app.context.users:
        logger.info('{} web users are defined.', len(app.context.users))
    else:
        logger.warning('No users are defined in the configuration. You will not be able to access the web interface.')

    app.context.background_task = app.loop.create_task(run_channels(app))


async def import_configuration(app: web.Application) -> Optional[ModuleType]:
    """Download and import configuration."""
    context = app.context
    logger.info('Importing configuration from {}', context.configuration_url)
    try:
        async with ClientSession(headers=[('Cache-Control', 'no-cache')]) as session:
            async with session.get(context.configuration_url) as response:
                return import_from_string('configuration', await response.text())
    except Exception as e:
        logger.error('Failed to import configuration: "{e}".', e=e)


async def on_cleanup(app: web.Application):
    """Cancel and close everything."""
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
    main(auto_envvar_prefix='IFTTTIE')
