from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Update:
    key: str
    value: Any = None


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
