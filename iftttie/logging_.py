from __future__ import annotations

import functools
import logging
import sys
from typing import Any, Callable, Optional

from loguru import logger

from iftttie.constants import LOGURU_FORMAT, VERBOSITY_LEVELS


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


def logged(
    enter_message: Optional[str] = None,
    success_message: Optional[str] = None,
    error_message: Optional[str] = None,
):
    """
    Wraps the function so that the messages and errors are logged when it's called.
    """

    def make_wrapper(function: Callable[..., Any]):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            if enter_message:
                logger.info(enter_message, *args, **kwargs)
            try:
                return_ = function(*args, **kwargs)
            except Exception as e:
                if error_message:
                    logger.error('{}: {}', error_message, e)
                raise
            else:
                if success_message:
                    logger.info(success_message, *args, **kwargs)
                return return_
        return wrapper

    return make_wrapper
