from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from iftttie.enums import Unit


@dataclass
class Update:
    key: str
    value: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now().astimezone())
    unit: Unit = Unit.OTHER
    title: Optional[str] = None
