from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from time import time
from typing import Any, Optional

from iftttie.enums import Unit


@dataclass
class Update:
    # Key is similar to "channel" in other automation assistants.
    # It's a unique identifier of some observed value.
    key: str

    # ID is used to de-duplicate updates for the same `key`.
    # If the same key-ID pairs occur twice, they're treated as the same.
    # This has a huge impact on the database size.
    id_: str = field(default_factory=lambda: str(int(time())))

    # The value itself. Usually, some primitive.
    value: Any = None

    # Time and date when the value was registered.
    timestamp: datetime = field(default_factory=lambda: datetime.now().astimezone())

    # Unit of the value.
    unit: Unit = Unit.OTHER

    # Title in the web interface.
    title: Optional[str] = None
