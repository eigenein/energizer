from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from iftttie.enums import ValueKind


@dataclass
class Update:
    key: str
    value: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now().astimezone())
    kind: ValueKind = ValueKind.OTHER


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
