from __future__ import annotations

import logging
from asyncio import Queue

import aiohttp_jinja2
import click
from aiohttp import web
from jinja2 import PackageLoader, select_autoescape

from iftttie import utils
from iftttie.core import start_queue, stop_queue
from iftttie.web import routes

logger = logging.getLogger('iftttie')


@click.command()
@click.option('--http-port', type=int, default=8080, help='HTTP dashboard and API port.')
def main(http_port: int):
    utils.setup_logging()

    logger.info('Starting IFTTTie…')
    app = web.Application()
    app['event_queue'] = Queue(maxsize=1000)  # TODO: option.

    # Setup queue.
    # TODO: run initialisation script.
    app.on_startup.append(start_queue)
    app.on_cleanup.append(stop_queue)

    # Start app.
    aiohttp_jinja2.setup(app, loader=PackageLoader('iftttie'), autoescape=select_autoescape())
    app.add_routes(routes)
    web.run_app(app, port=http_port, print=None)

    logger.info('IFTTTie stopped.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
