from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, validator


class Unit(str, Enum):
    BEAUFORT = 'BEAUFORT'
    BOOLEAN = 'BOOLEAN'
    CELSIUS = 'CELSIUS'
    DATETIME = 'DATETIME'  # timestamp
    ENUM = 'ENUM'
    HPA = 'HPA'  # hPa
    IMAGE_URL = 'IMAGE_URL'
    JPEG = 'JPEG'  # bytes
    MPS = 'MPS'  # m/s
    RH = 'RH'  # relative humidity
    TEXT = 'TEXT'
    TIMEDELTA = 'TIMEDELTA'  # seconds
    WATT = 'WATT'

    @property
    def is_logged(self) -> bool:
        """
        Is value of this type stored in a log collection.
        """
        return self not in (Unit.IMAGE_URL, Unit.JPEG)

    @property
    def is_stored(self) -> bool:
        """
        Is value of this type stored in the `actual` collection.
        """
        return self not in (Unit.JPEG,)

    @property
    def is_float(self) -> bool:
        return self in (Unit.BEAUFORT, Unit.CELSIUS, Unit.HPA, Unit.MPS, Unit.RH, Unit.WATT, Unit.TIMEDELTA)


class Event(BaseModel):
    value: Any

    # Timestamp is set to now by default.
    timestamp: datetime = None

    # Channel ID is not saved in the logs.
    channel: Optional[str] = None

    # Unit is not saved in the logs.
    unit: Optional[Unit] = None

    # Title is not saved in the logs.
    title: Optional[str] = None

    @property
    def display_title(self) -> str:
        return self.title or self.channel

    # noinspection PyMethodParameters
    @validator('timestamp', pre=True, always=True)
    def set_default_timestamp(cls, value: Optional[datetime]):
        """
        Sets the current timestamp by default.
        """
        return value or datetime.now(timezone.utc)
