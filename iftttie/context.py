from __future__ import annotations

from asyncio import create_task
from dataclasses import dataclass
from typing import Mapping

from loguru import logger
from sqlitemap import Connection

from iftttie.automation import Automation
from iftttie.constants import ACTUAL_KEY
from iftttie.helpers import call_handler
from iftttie.types_ import Event


@dataclass
class Context:
    # Database connection.
    db: Connection

    # User-defined automation
    automation: Automation

    def get_actual(self) -> Mapping[str, Event]:
        """
        Get actual sensor values.
        """
        return {key: Event(**value) for key, value in self.db[ACTUAL_KEY].items()}

    def trigger_event(self, event: Event):
        """
        Handle a single event in the application context.
        """
        logger.info('{key} = {value!r}', key=event.channel_id, value=event.value)
        previous = self.db[ACTUAL_KEY].get(event.channel_id)

        with self.db:
            self.db[ACTUAL_KEY][event.channel_id] = event.dict()
            if event.is_logged:
                # Historical value uses optimised representation.
                self.db[f'log:{event.channel_id}'][event.key] = event.dict(include={'timestamp', 'value'})

        previous = Event(**previous) if previous is not None else None
        # noinspection PyAsyncCall
        create_task(call_handler(self.automation.on_event(event=event, previous=previous, actual=self.get_actual())))
