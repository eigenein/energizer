from __future__ import annotations

from enum import Enum


class Unit(str, Enum):
    BEAUFORT = 'BEAUFORT'
    BOOLEAN = 'BOOLEAN'
    CELSIUS = 'CELSIUS'
    DATETIME = 'DATETIME'
    ENUM = 'ENUM'
    HPA = 'HPA'  # hPa
    HUMIDITY = 'HUMIDITY'
    IMAGE_URL = 'IMAGE_URL'
    MPS = 'MPS'  # m/s
    OTHER = 'OTHER'
    TIMEDELTA = 'TIMEDELTA'
    WATT = 'WATT'
