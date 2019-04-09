from __future__ import annotations

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
