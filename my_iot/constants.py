from __future__ import annotations

from datetime import timedelta

import umsgpack
from aiohttp import ClientTimeout
from pkg_resources import resource_string

LOGURU_FORMAT = ' '.join((
    '<green>{time:MMM DD HH:mm:ss}</green>',
    '<cyan>({name}:{line})</cyan>',
    '<level>[{level:.1}]</level>',
    '<level>{message}</level>',
))

# Number of `-v` options to log level.
VERBOSITY_LEVELS = {
    0: 'ERROR',
    1: 'WARNING',
    2: 'INFO',
    3: 'DEBUG',
}

# Collection with the actual sensor values.
ACTUAL_KEY = 'actual'

HTTP_PORT = 8080
HTTP_TIMEOUT = ClientTimeout(total=10.0)

DATABASE_OPTIONS = {
    'dumps_': umsgpack.packb,
    'loads_': umsgpack.unpackb,
    'check_same_thread': False,
}

STATICS = {
    name: resource_string('my_iot', f'static/{name}')
    for name in [
        'android-chrome-192x192.png',
        'android-chrome-512x512.png',
        'apple-touch-icon.png',
        'favicon.ico',
        'favicon-16x16.png',
        'favicon-32x32.png',
        'site.webmanifest',
    ]  # TODO: should go to `constants`.
}

DEFAULT_PERIOD = timedelta(minutes=5)

MAX_CHART_POINTS = 500
