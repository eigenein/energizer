from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ChannelEvent:
    key: str
    value_1: Any = None  # IFTTT `value1`
    value_2: Any = None  # IFTTT `value2`
    value_3: Any = None  # IFTTT `value3`


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
