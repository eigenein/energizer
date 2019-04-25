from __future__ import annotations

from aiohttp import ClientTimeout

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

HTTP_TIMEOUT = ClientTimeout(total=10.0)
