from __future__ import annotations

from typing import Awaitable, TypeVar

from loguru import logger

T = TypeVar('T')


async def call_handler(awaitable: Awaitable[T]) -> T:
    try:
        return await awaitable
    except Exception as e:
        logger.opt(exception=e).error('Error while calling the handler.')
