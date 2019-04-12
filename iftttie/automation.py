from __future__ import annotations

from abc import ABCMeta
from typing import Any, List, Mapping, Optional, Tuple

from iftttie.services.base import Service
from iftttie.types_ import Event


class Automation(metaclass=ABCMeta):
    """
    Base class for your automation setups.
    """

    def __init__(self):
        self.services: List[Service] = []
        self.users: List[Tuple[str, str]] = []

    async def on_startup(self) -> None:
        """
        Startup handler. Called when the app is starting up.
        """

    async def on_event(
        self,
        *,
        event: Event,
        previous: Optional[Event],
        actual: Mapping[str, Event],
        **kwargs: Any,
    ) -> None:
        """
        Event handler which is called on every single event occurred in a channel.
        :arg event: event itself.
        :arg previous: previous event with the same channel ID, if any.
        :arg actual: actual events for all the services IDs.
        """

    async def on_cleanup(self) -> None:
        """
        Cleanup handler. Called when the app is shutting down.
        """
