from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any

from iftttie import web


class BaseChannel(metaclass=ABCMeta):
    @abstractmethod
    async def run(self, context: web.Context, **kwargs: Any):
        """
        Runs the channel. May raise unhandled exceptions.
        """
        raise NotImplementedError()
