from __future__ import annotations

import logging
from asyncio import Queue
from typing import Optional, Tuple

import click
from aiohttp import web

from iftttie import middleware, utils
from iftttie.core import handle_event_queue
from iftttie.web import routes

logger = logging.getLogger('iftttie')


@click.command()
@click.option('--http-port', type=int, default=8080, help='HTTP port.')
@click.option('access_tokens', '--access-token', type=str, required=True, multiple=True, help='IFTTTie access token.')
@click.option('--ifttt-token', type=str, default=None, help='IFTTT Webhooks token.')
@click.option('--nest-token', type=str, default=None, help='NEST API OAuth token.')
@click.option('--buienradar-station-id', type=int, default=None, help='Buienradar.nl station ID.')
def main(
    http_port: int,
    access_tokens: Tuple[str, ...],
    ifttt_token: Optional[str],
    nest_token: Optional[str],
    buienradar_station_id: Optional[int],
):
    utils.setup_logging()

    logger.info('🛫 Starting IFTTTie…')
    app = web.Application(middlewares=[middleware.authenticate])
    app['access_tokens'] = access_tokens
    app['event_queue'] = Queue(maxsize=1000)  # TODO: option.
    app.add_routes(routes)
    app.on_startup.append(start_event_handler)
    app.on_cleanup.append(stop_event_handler)

    web.run_app(app, port=http_port, print=None)

    logger.info('🛬 IFTTTie stopped.')


async def start_event_handler(app: web.Application):
    logger.info('🛫 Starting event queue…')
    app['handle_event_queue'] = app.loop.create_task(handle_event_queue(app['event_queue']))


async def stop_event_handler(app: web.Application):
    logger.info('🛫 Stopping event queue…')
    app['handle_event_queue'].cancel()
    await app['handle_event_queue']


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
