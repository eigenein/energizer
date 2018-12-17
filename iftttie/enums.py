from __future__ import annotations

from enum import Enum


class ValueKind(str, Enum):
    BFT = 'BFT'  # Beaufort
    CELSIUS = 'CELSIUS'
    HPA = 'HPA'  # hPa
    HUMIDITY = 'HUMIDITY'
    IMAGE_URL = 'IMAGE_URL'
    MPS = 'MPS'  # m/s
    ON_OFF = 'ON_OFF'
    RAW = 'RAW'
    YES_NO = 'YES_NO'
