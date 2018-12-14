from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import AsyncIterator

from aiohttp import web

from iftttie.dataclasses_ import Update


class BaseService(metaclass=ABCMeta):
    @abstractmethod
    async def yield_updates(self, app: web.Application) -> AsyncIterator[Update]:
        raise NotImplementedError()
