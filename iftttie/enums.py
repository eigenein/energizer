from __future__ import annotations

from enum import Enum


class ValueKind(str, Enum):
    BEAUFORT = 'BEAUFORT'
    CELSIUS = 'CELSIUS'
    HPA = 'HPA'  # hPa
    HUMIDITY = 'HUMIDITY'
    IMAGE_URL = 'IMAGE_URL'
    MPS = 'MPS'  # m/s
    BOOLEAN = 'BOOLEAN'
    OTHER = 'OTHER'
