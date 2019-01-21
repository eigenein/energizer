from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any

from iftttie import web


class BaseService(metaclass=ABCMeta):
    @abstractmethod
    async def run(self, context: web.Context, **kwargs: Any):
        """
        Runs the service. May raise unhandled exceptions.
        """
        raise NotImplementedError()
