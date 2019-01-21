from __future__ import annotations

from asyncio.tasks import gather, sleep
from concurrent.futures import CancelledError
from contextlib import suppress

from aiohttp import ClientConnectorError
from loguru import logger

from iftttie import web
from iftttie.services.base import BaseService


async def run_services(app: web.Application):
    """Run services from the configuration."""

    logger.info('Running services…')
    with suppress(CancelledError):
        await gather(*(run_service(app, service) for service in app.context.services))


async def run_service(app: web.Application, service: BaseService):
    while True:
        logger.info('Running {service}…', service=service)
        try:
            await service.run(app.context)
        except CancelledError:
            logger.debug('Stopped service {service}.', service=service)
            break
        except ClientConnectorError as e:
            logger.error('{service} has raised a connection error:', service=service)
            logger.error('{e}', e=e)
        except Exception as e:
            logger.opt(exception=e).error('{service} has failed.', service=service)
        logger.error('Restarting in a minute.')
        await sleep(60.0)
