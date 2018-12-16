from __future__ import annotations

from enum import Enum


class ValueKind(Enum):
    HUMIDITY = 'HUMIDITY'
    ON_OFF = 'ON_OFF'
    RAW = 'RAW'
    TEMPERATURE = 'TEMPERATURE'
    YES_NO = 'YES_NO'
