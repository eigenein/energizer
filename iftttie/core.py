from __future__ import annotations

from asyncio.tasks import gather, sleep
from concurrent.futures import CancelledError
from contextlib import suppress

from aiohttp import ClientConnectorError
from loguru import logger

from iftttie import web
from iftttie.channels.base import BaseChannel


async def run_channels(app: web.Application):
    """Run channels from the configuration."""

    logger.info('Running channels…')
    with suppress(CancelledError):
        await gather(*(run_channel(app, channel) for channel in app.context.channels))


async def run_channel(app: web.Application, channel: BaseChannel):
    while True:
        logger.info('Running {channel}…', channel=channel)
        try:
            await channel.run(app.context)
        except CancelledError:
            logger.debug('Stopped channel {channel}.', channel=channel)
            break
        except ClientConnectorError as e:
            logger.error('{channel} has raised a connection error:', channel=channel)
            logger.error('{e}', e=e)
        except Exception as e:
            logger.opt(exception=e).error('{channel} has failed.', channel=channel)
        logger.error('Restarting in a minute.')
        await sleep(60.0)
