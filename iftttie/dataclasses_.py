from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pickle import loads
from sqlite3 import Row
from typing import Any, Optional

from iftttie.enums import ValueKind


@dataclass
class Update:
    key: str
    value: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now().astimezone())
    kind: ValueKind = ValueKind.OTHER

    @staticmethod
    def from_row(row: Row) -> Update:
        return Update(
            key=row['key'],
            value=loads(row['value']),
            timestamp=datetime.fromtimestamp(row['timestamp'] / 1000).astimezone(),
            kind=ValueKind(row['kind']),
        )


@dataclass
class ServerSideEvent:
    name: Optional[str]
    data: str = ''
