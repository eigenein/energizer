from __future__ import annotations

from abc import ABCMeta, abstractmethod

from aiohttp import web


class BaseService(metaclass=ABCMeta):
    @abstractmethod
    async def run(self, app: web.Application):
        raise NotImplementedError()
