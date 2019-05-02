from __future__ import annotations

from typing import Any, List

from my_iot.constants import MAX_CHART_POINTS
from my_iot.types_ import Event

format_timestamp = '{:%Y-%m-%d %H:%M:%S.%f}'.format


def make_float_chart(events: List[Event]) -> Any:
    # Limit number of points.
    # FIXME: more efficient implementation needed, perhaps add a limit parameter to `sqlitemap`.
    step = (len(events) + MAX_CHART_POINTS) // MAX_CHART_POINTS
    events = events[::step]
    return [{
        'type': 'scatter',
        'line': {'shape': 'spline'},
        'x': [format_timestamp(event.timestamp) for event in events],
        'y': [event.value for event in events],
    }]
