from __future__ import annotations

from abc import ABCMeta, abstractmethod


class BaseChannel(metaclass=ABCMeta):
    @property
    @abstractmethod
    async def events(self):
        """
        Gets an asynchronous generator of events.
        """
        raise NotImplementedError()
