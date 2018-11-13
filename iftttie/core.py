from __future__ import annotations

import logging
from typing import Awaitable

from aiohttp import web

logger = logging.getLogger(__name__)


def append_background_task(app: web.Application, key: str, coro: Awaitable):
    """Append background task to aiohttp app."""

    async def start_handler(app_: web.Application):
        logger.info(f'Starting {key}…')
        app_[key] = app_.loop.create_task(coro)

    async def stop_handler(app_: web.Application):
        logger.info(f'Stopping {key}…')
        app_[key].cancel()
        await app_[key]

    app.on_startup.append(start_handler)
    app.on_cleanup.append(stop_handler)
