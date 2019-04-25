from __future__ import annotations

import ssl
import sys
from asyncio import create_task
from typing import Optional

import click
import pkg_resources
import umsgpack
from aiohttp.web import Application
from loguru import logger
from sqlitemap import Connection

from myiot import web
from myiot.automation import Automation
from myiot.helpers import call_handler
from myiot.logging_ import init_logging
from myiot.runner import run_services
from myiot.types_ import Event, Unit
from myiot.web import Context


def option(*args, **kwargs):
    return click.option(*args, show_envvar=True, **kwargs)


@click.command(context_settings={'max_content_width': 120})
@click.argument(
    'automation_path',
    envvar='MY_IOT_AUTOMATION_PATH',
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
)
@option(
    'cert_path', '--cert',
    envvar='MY_IOT_CERT_PATH',
    help='Server certificate path.',
    type=click.Path(exists=True, dir_okay=False),
)
@option(
    'key_path', '--key',
    envvar='MY_IOT_KEY_PATH',
    help='Server private key path.',
    type=click.Path(exists=True, dir_okay=False),
)
@option(
    'verbosity', '-v', '--verbose',
    count=True,
    envvar='MY_IOT_VERBOSITY',
    help='Logging verbosity.',
)
@option(
    'port', '-p', '--port',
    default=8443,
    envvar='MY_IOT_PORT',
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
    logger.info('Starting My IoT…')

    # noinspection PyBroadException
    try:
        automation = import_automation(automation_path)
    except Exception as e:
        logger.opt(exception=e).error('Failed to import the automation.')
        automation = None

    if cert_path and key_path:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(cert_path, key_path)
    else:
        ssl_context = None

    db = Connection('db.sqlite3', dumps_=umsgpack.packb, loads_=umsgpack.unpackb)
    web.start(ssl_context, port, Context(db=db, automation=automation), on_startup, on_cleanup)
    logger.info('My IoT stopped.')


async def on_startup(app: Application):
    """
    Set up the web application.
    """
    context: Context = app['context']
    await call_handler(context.automation.on_startup())
    context.trigger_event(Event(
        value=pkg_resources.get_distribution('myiot').version,
        channel_id='my-iot:version',
        unit=Unit.TEXT,
        title='My IoT version',
    ))
    # noinspection PyAsyncCall
    create_task(run_services(context))


def import_automation(path: str) -> Automation:
    logger.info('Importing automation from {}…', path)
    sys.path.append(path)
    # noinspection PyUnresolvedReferences, PyPackageRequirements
    from automation import MyAutomation
    return MyAutomation()


async def on_cleanup(app: Application):
    """
    Cancel and close everything.
    """
    logger.info('Cleaning up…')
    await call_handler(app['context'].automation.on_cleanup())
    app['context'].db.close()


if __name__ == '__main__':
    main()
