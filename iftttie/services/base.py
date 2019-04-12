from __future__ import annotations

from abc import ABCMeta, abstractmethod


class Service(metaclass=ABCMeta):
    @property
    @abstractmethod
    async def events(self):
        """
        Gets an asynchronous generator of events.
        """
        raise NotImplementedError()
