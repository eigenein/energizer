from __future__ import annotations

from asyncio.tasks import gather, sleep
from concurrent.futures import CancelledError

from aiohttp import ClientConnectorError
from loguru import logger

from iftttie.channels.base import BaseChannel
from iftttie.context import Context


async def run_channels(context: Context):
    """
    Run channels from the configuration.
    """

    logger.info('Running channels…')
    await gather(*[run_channel(context, channel) for channel in context.channels])


async def run_channel(context: Context, channel: BaseChannel):
    """
    Run the single channel.
    """
    while True:
        logger.info('Running {channel}…', channel=channel)
        try:
            async for event in channel.events:
                # TODO: reset error counter.
                await context.trigger_event(event)
        except CancelledError:
            logger.info('Stopped channel {channel}.', channel=channel)
            break
        except (ConnectionError, ClientConnectorError) as e:
            logger.error('{channel} has raised a connection error:', channel=channel)
            logger.error('{e}', e=e)
        except Exception as e:
            logger.opt(exception=e).error('{channel} has failed.', channel=channel)
        else:
            pass  # TODO: reset error counter.
        logger.error('Restarting in a minute.')
        await sleep(60.0)  # TODO: something smarter, depending on the counter.
