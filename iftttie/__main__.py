from __future__ import annotations

import logging
from asyncio import Queue

import click
from aiohttp import web

from iftttie import ifttt, middleware, utils
from iftttie.core import append_background_task
from iftttie.event_sources import nest
from iftttie.web import routes

logger = logging.getLogger('iftttie')


@click.command()
@click.option('--http-port', type=int, default=8080, help='HTTP port.')
@click.option('access_tokens', '--access-token', type=str, required=True, multiple=True, help='IFTTTie access token.')
@click.option('--ifttt-token', type=str, required=True, help='IFTTT Webhooks token.')
@click.option('--nest-token', type=str, default=None, help='NEST API OAuth token.')
@click.option('--buienradar-station-id', type=int, default=None, help='Buienradar.nl station ID.')
def main(http_port: int, **kwargs):
    utils.setup_logging()

    logger.info('Starting IFTTTie…')
    app = web.Application(middlewares=[middleware.authenticate])
    for key, value in kwargs.items():
        app[key] = value
    app['event_queue'] = Queue(maxsize=1000)  # TODO: option.
    app.add_routes(routes)

    append_background_task(app, 'ifttt.run', ifttt.run(app))
    append_background_task(app, 'nest.run', nest.run(app))

    web.run_app(app, port=http_port, print=None)

    logger.info('IFTTTie stopped.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
