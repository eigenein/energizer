from __future__ import annotations

from enum import Enum


class ValueKind(Enum):
    BFT = 'BFT'
    CELSIUS = 'CELSIUS'
    HPA = 'HPA'
    HUMIDITY = 'HUMIDITY'
    IMAGE_URL = 'IMAGE_URL'
    ON_OFF = 'ON_OFF'
    RAW = 'RAW'
    YES_NO = 'YES_NO'
