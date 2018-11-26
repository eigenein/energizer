from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ChannelEvent:
    key: str
    value: Any = None


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
