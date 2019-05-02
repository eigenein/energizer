from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Mapping

from sqlitemap import Connection

from my_iot.constants import ACTUAL_KEY
from my_iot.types_ import Event

EVENT_INCLUDE = {'timestamp', 'value'}  # logged value uses optimised representation


def timestamp_key(timestamp: datetime) -> str:
    """
    Get the key under which the timestamp is stored in a collection.
    Supposed to be monotonic (non-decreasing).
    """
    return timestamp.astimezone(timezone.utc).strftime('%Y%m%d%H%M%S%f')


def save_event(db: Connection, event: Event) -> None:
    with db:
        if event.unit.is_stored:
            db[ACTUAL_KEY][event.channel] = event.dict()
        if event.unit.is_logged:
            db[f'log:{event.channel}'][timestamp_key(event.timestamp)] = event.dict(include=EVENT_INCLUDE)


def get_actual(db: Connection) -> Mapping[str, Event]:
    """
    Get actual channel values.
    """
    return {key: Event(**value) for key, value in db[ACTUAL_KEY].items()}


def get_log(db: Connection, channel: str, period: timedelta) -> List[Event]:
    """
    Gets the channel log within the specified period until now.
    """
    return [
        Event(**event)
        for event in db[f'log:{channel}'][timestamp_key(datetime.now() - period):]
    ]
