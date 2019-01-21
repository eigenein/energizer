from __future__ import annotations

import ssl
from types import ModuleType
from typing import Optional, Sequence, Tuple

import click
from aiohttp import ClientSession
from loguru import logger

from iftttie import web
from iftttie.core import run_queue
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
    'users', '-u', '--user',
    type=click.Tuple([str, str]),
    multiple=True,
    required=True,
    envvar='IFTTTIE_USERS',
    show_envvar=True,
    help='User password hash. Use `iftttie.utils password-hash` to obtain it.',
)
@click.option(
    'verbosity', '-v', '--verbose',
    count=True,
    envvar='IFTTTIE_VERBOSITY',
    show_envvar=True,
    help='Logging verbosity.',
)
def main(
    configuration_url: str,
    cert_path: Optional[str],
    key_path: Optional[str],
    users: Sequence[Tuple[str, str]],
    verbosity: int,
):
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

    web.start(ssl_context, Context(configuration_url=configuration_url, users=users), on_startup, on_cleanup)
    logger.success('IFTTTie stopped.')


async def on_startup(app: web.Application):
    """Import configuration, run services and return async tasks."""
    app.context.db = init_database('db.sqlite3')
    app.context.session = await ClientSession(raise_for_status=True).__aenter__()
    app.context.configuration = await import_configuration(app)
    app.context.run_queue_task = app.loop.create_task(run_queue(app))


async def import_configuration(app: web.Application) -> Optional[ModuleType]:
    """Download and import configuration."""
    logger.info('Importing configuration from {}...', app.context.configuration_url)
    try:
        async with app.context.session.get(app.context.configuration_url, headers=[('Cache-Control', 'no-cache')]) as response:
            return import_from_string('configuration', await response.text())
    except Exception as e:
        logger.error('Failed to import configuration: "{e}".', e=e)


async def on_cleanup(app: web.Application):
    """Cancel and close everything."""
    logger.info('Stopping event queue…')
    app.context.run_queue_task.cancel()
    await app.context.run_queue_task
    await app.context.session.close()
    app.context.db.close()
    logger.info('Event queue stopped.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
