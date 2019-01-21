from __future__ import annotations

from abc import ABCMeta, abstractmethod
from asyncio import Queue
from typing import Any

from aiohttp import ClientSession

from iftttie.types import Update


class BaseService(metaclass=ABCMeta):
    @abstractmethod
    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        """
        Runs the service. May raise unhandled exceptions.
        """
        raise NotImplementedError()
