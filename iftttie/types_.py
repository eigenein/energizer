from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, validator

utc = timezone.utc


class Unit(str, Enum):
    BEAUFORT = 'BEAUFORT'
    BOOLEAN = 'BOOLEAN'
    CELSIUS = 'CELSIUS'
    DATETIME = 'DATETIME'
    ENUM = 'ENUM'
    HPA = 'HPA'  # hPa
    IMAGE_URL = 'IMAGE_URL'
    MPS = 'MPS'  # m/s
    RH = 'RH'  # relative humidity
    TEXT = 'TEXT'
    TIMEDELTA = 'TIMEDELTA'
    WATT = 'WATT'


class Event(BaseModel):
    key: str
    value: Any = None
    timestamp: datetime = None
    unit: Unit = Unit.TEXT
    title: Optional[str] = None

    # TODO: rename it, perhaps to just `key` when the latter becomes `channel` or so.
    @property
    def db_key(self) -> str:
        """
        Get the key under which the event is stored in a collection.
        Supposed to be monotonic (non-decreasing).
        """
        return self.timestamp.astimezone(utc).strftime('%Y%m%d%H%M%S%f')

    # noinspection PyMethodParameters
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, value: Optional[datetime]):
        """
        Sets the current timestamp by default.
        """
        return value or datetime.now(utc)
