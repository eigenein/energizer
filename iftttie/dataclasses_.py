from dataclasses import dataclass
from typing import Any


@dataclass
class Event:
    key: str
    value: Any
