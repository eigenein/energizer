from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import AsyncIterable

from my_iot.types_ import Event


class Service(metaclass=ABCMeta):
    @property
    @abstractmethod
    async def events(self) -> AsyncIterable[Event]:
        """
        Gets an asynchronous generator of events.
        """
        raise NotImplementedError()
        # noinspection PyUnreachableCode
        yield NotImplemented

    # TODO: `close` method to allow freeing up resources like a `ClientSession`.
