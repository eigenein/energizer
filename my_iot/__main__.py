from __future__ import annotations

import ssl
from asyncio import create_task
from pathlib import Path
from types import ModuleType
from typing import Optional

import click
import pkg_resources
import umsgpack
from aiohttp.web import Application
from loguru import logger
from sqlitemap import Connection

from my_iot import web
from my_iot.imp_ import create_module
from my_iot.logging_ import init_logging
from my_iot.runner import run_services
from my_iot.types_ import Event, Unit
from my_iot.web import Context


def option(*args, **kwargs):
    return click.option(*args, show_envvar=True, **kwargs)


@click.command(context_settings={'max_content_width': 120})
@click.argument(
    'automation_path',
    envvar='MY_IOT_AUTOMATION_PATH',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
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

    automation = import_automation(Path(automation_path))

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
    context.trigger_event(Event(
        value=pkg_resources.get_distribution('my_iot').version,
        channel='my_iot:version',
        unit=Unit.TEXT,
        title='My IoT version',
    ))
    # noinspection PyAsyncCall
    create_task(run_services(context))


def import_automation(path: Path) -> ModuleType:
    logger.info('Importing automation from {}…', path)
    return create_module(name='automation', source=path.read_text(encoding='utf-8'))


async def on_cleanup(app: Application):
    """
    Cancel and close everything.
    """
    logger.info('Cleaning up…')
    await app['context'].close()


if __name__ == '__main__':
    main()
