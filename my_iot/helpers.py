from __future__ import annotations

from datetime import datetime, timezone

utc = timezone.utc


def timestamp_key(timestamp: datetime) -> str:
    """
    Get the key under which the timestamp is stored in a collection.
    Supposed to be monotonic (non-decreasing).
    """
    return timestamp.astimezone(utc).strftime('%Y%m%d%H%M%S%f')
