from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from iftttie.utils import now


@dataclass
class Update:
    key: str
    value: Any = None
    timestamp: datetime = field(default_factory=now)


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
