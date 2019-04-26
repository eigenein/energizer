from __future__ import annotations

import asyncio
from asyncio.tasks import gather, sleep
from concurrent.futures import CancelledError
from datetime import timedelta

from aiohttp import ClientConnectorError
from loguru import logger

from my_iot.context import Context
from my_iot.services.base import Service

# TODO: perhaps merge this with `Context`.


async def run_services(context: Context):
    """
    Run services from the configuration.
    """

    logger.info('Running services…')
    try:
        await gather(*[run_service(context, service) for service in context.services])
    except CancelledError:
        pass  # TODO: close all services.
    except Exception as e:
        logger.opt(exception=e).critical('Failed to run services.')


async def run_service(context: Context, service: Service):
    """
    Run the single service.
    """
    n_errors = 0
    while True:
        logger.info('Running {}…', service)
        try:
            async for event in service.events:
                n_errors = 0  # the service successfully generated an event
                context.trigger_event(event)
                await sleep(0)  # force task switch
        except CancelledError:
            logger.info('Stopped service {}.', service)
            break
        # FIXME: refactor the following 2 `except` clauses.
        except (ConnectionError, ClientConnectorError, asyncio.TimeoutError) as e:
            logger.error('{} has raised a connection error: {}', service, e)
            n_errors += 1
        except Exception as e:
            logger.opt(exception=e).error('{} has failed.', service)
            n_errors += 1
        else:
            n_errors = 0  # the service normally returned
        if n_errors:
            delay = 2.0 ** min(n_errors, 16)
            logger.error('Restarting in {}…', timedelta(seconds=delay))
            await sleep(delay)
