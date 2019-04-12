from __future__ import annotations

import ssl
import sys
from asyncio import create_task
from typing import Optional

import click
import umsgpack
from aiohttp.web import Application
from loguru import logger
from sqlitemap import Connection

from iftttie import web
from iftttie.automation import Automation
from iftttie.logging_ import init_logging, logged
from iftttie.runner import run_services
from iftttie.web import Context


def option(*args, **kwargs):
    return click.option(*args, show_envvar=True, **kwargs)


@click.command(context_settings={'max_content_width': 120})
@click.argument(
    'automation_path',
    envvar='IFTTTIE_AUTOMATION_PATH',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@option(
    'cert_path', '--cert',
    envvar='IFTTTIE_CERT_PATH',
    help='Server certificate path.',
    type=click.Path(exists=True, dir_okay=False),
)
@option(
    'key_path', '--key',
    envvar='IFTTTIE_KEY_PATH',
    help='Server private key path.',
    type=click.Path(exists=True, dir_okay=False),
)
@option(
    'verbosity', '-v', '--verbose',
    count=True,
    envvar='IFTTTIE_VERBOSITY',
    help='Logging verbosity.',
)
@option(
    'port', '-p', '--port',
    default=8443,
    envvar='IFTTTIE_PORT',
    help='Web interface and webhook API port.',
    show_default=True,
    type=int,
)
def main(
    automation_path: str,
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

    # noinspection PyBroadException
    try:
        automation = import_automation(automation_path)
    except Exception:
        automation = None

    if cert_path and key_path:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(cert_path, key_path)
    else:
        ssl_context = None

    db = Connection('db.sqlite3', dumps_=umsgpack.packb, loads_=umsgpack.unpackb)
    web.start(ssl_context, port, Context(db=db, automation=automation), on_startup, on_cleanup)
    logger.info('IFTTTie stopped.')


async def on_startup(app: Application):
    """
    Set up the web application.
    """
    # noinspection PyAsyncCall
    create_task(run_services(app['context']))


@logged(
    enter_message='Importing automation from {}…',
    success_message='Successfully imported the automation.',
    error_message='Error occurred while importing the automation',
)
def import_automation(path: str) -> Automation:
    sys.path.append(path)
    # noinspection PyUnresolvedReferences, PyPackageRequirements
    from automation import MyAutomation
    return MyAutomation()


async def on_cleanup(app: Application):
    """
    Cancel and close everything.
    """
    try:
        await app['context'].automation.on_cleanup()
    except Exception as e:
        logger.opt(exception=e).error('The error occurred in `on_cleanup` handler.')
    else:
        logger.info('Cleaned up the automation.')
    app['context'].db.close()
    logger.info('Database is closed.')


if __name__ == '__main__':
    main()
