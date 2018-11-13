from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Event:
    key: str
    value_1: Any = None
    value_2: Any = None
    value_3: Any = None


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
