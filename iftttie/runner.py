from __future__ import annotations

from asyncio.tasks import gather, sleep
from concurrent.futures import CancelledError

from aiohttp import ClientConnectorError
from loguru import logger

from iftttie.services.base import Service
from iftttie.context import Context


async def run_services(context: Context):
    """
    Run services from the configuration.
    """

    logger.info('Running services…')
    try:
        await gather(*[run_service(context, service) for service in context.automation.services])
    except CancelledError:
        pass
    except Exception as e:
        logger.opt(exception=e).critical('Failed to run services.')


async def run_service(context: Context, service: Service):
    """
    Run the single service.
    """
    while True:
        logger.info('Running {}…', service)
        try:
            async for event in service.events:
                # TODO: reset error counter.
                context.trigger_event(event)
        except CancelledError:
            logger.info('Stopped service {}.', service)
            break
        except (ConnectionError, ClientConnectorError) as e:
            logger.error('{} has raised a connection error:', service)
            logger.error('{e}', e=e)
        except Exception as e:
            logger.opt(exception=e).error('{} has failed.', service)
        else:
            pass  # TODO: reset error counter.
        logger.error('Restarting in a minute.')
        await sleep(60.0)  # TODO: something smarter, depending on the counter.
