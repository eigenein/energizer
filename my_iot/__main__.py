from __future__ import annotations

from asyncio import create_task
from pathlib import Path
from types import ModuleType

import click
import pkg_resources
from aiohttp.web import Application
from loguru import logger
from sqlitemap import Connection

from my_iot import web
from my_iot.constants import DATABASE_OPTIONS
from my_iot.imp_ import create_module
from my_iot.logging_ import init_logging
from my_iot.types_ import Event, Unit
from my_iot.web import Context


def option(*args, **kwargs):
    return click.option(*args, show_envvar=True, **kwargs)


@click.command(context_settings={'max_content_width': 120})
@click.argument(
    'automation_path',
    envvar='MY_IOT_AUTOMATION_PATH',
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
    default='automation.py',
)
@option(
    'verbosity', '-v', '--verbose',
    count=True,
    envvar='MY_IOT_VERBOSITY',
    help='Logging verbosity.',
)
def main(automation_path: str, verbosity: int):
    """
    Yet another home automation service.
    """
    init_logging(verbosity)
    logger.info('Starting My IoT…')
    automation = import_automation(Path(automation_path))
    db = Connection('db.sqlite3', **DATABASE_OPTIONS)
    web.start(Context(db=db, automation=automation), on_startup, on_cleanup)
    logger.info('My IoT stopped.')


async def on_startup(app: Application):
    """
    Set up the web application.
    """
    context: Context = app['context']
    await context.on_event(Event(
        value=pkg_resources.get_distribution('my_iot').version,
        channel='my_iot:version',
        unit=Unit.TEXT,
        title='My IoT version',
    ))
    # noinspection PyAsyncCall
    create_task(context.run_services())


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
