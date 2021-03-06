from __future__ import annotations

import logging
import sys

from loguru import logger

from my_iot.constants import LOGURU_FORMAT, VERBOSITY_LEVELS


class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages towards Loguru sinks.
    https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
    """
    def emit(self, record: logging.LogRecord):
        logger \
            .opt(depth=6, exception=record.exc_info) \
            .log(record.levelname, record.getMessage())


def init_logging(verbosity: int):
    logger.stop()
    logger.add(sys.stderr, format=LOGURU_FORMAT, level=VERBOSITY_LEVELS.get(verbosity, 'TRACE'), backtrace=False)
    logging.basicConfig(level=logging.NOTSET, handlers=[InterceptHandler()])
    logger.disable('aiosqlite.core')
