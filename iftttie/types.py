from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from time import time
from typing import Any, Optional


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


@dataclass
class Event:
    # Key is similar to "channel" in other automation assistants.
    # It's a unique identifier of some observed value.
    key: str

    # ID is used to de-duplicate events for the same `key`.
    # If the same key-ID pairs occur twice, they're treated as the same.
    # This has a huge impact on the database size.
    id_: str = field(default_factory=lambda: str(int(time())))

    # The value itself. Usually, some primitive.
    value: Any = None

    # Time and date when the value was registered.
    timestamp: datetime = field(default_factory=lambda: datetime.now().astimezone())

    # Unit of the value.
    unit: Unit = Unit.TEXT

    # Title in the web interface.
    title: Optional[str] = None
