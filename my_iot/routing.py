from __future__ import annotations

import re
from asyncio import CancelledError
from functools import wraps
from typing import Any, Awaitable, Callable, List, Mapping, Optional

from loguru import logger

from my_iot.types_ import Event

AsyncCallable = Callable[..., Awaitable]
Predicate = Callable[..., bool]
DecorateAsyncCallable = Callable[[AsyncCallable], AsyncCallable]


class EventRouter:
    """
    Routes events to their corresponding handlers in an automation module.
    """

    def __init__(self):
        self.handlers: List[AsyncCallable] = []

    def __call__(self, callable_: AsyncCallable):
        """
        Add the handler.
        """
        self.handlers.append(callable_)
        return callable_

    async def on_event(self, **kwargs: Any):
        for handler in self.handlers:
            try:
                await handler(**kwargs)
            except CancelledError:
                logger.warning('Handler `{}` was interrupted.', handler)
            except Exception as e:
                logger.opt(exception=e).error('Error in handler `{}`.', handler)


def if_(predicate: Predicate) -> DecorateAsyncCallable:
    """
    Decorates a handler so that it's only called when the predicate returns true.
    This is a generic function that can be used when no convenience shortcut is available.
    """
    def decorate(callable_: AsyncCallable) -> AsyncCallable:
        @wraps(callable_)
        async def wrapper(**kwargs):
            if predicate(**kwargs):
                return await callable_(**kwargs)
        return wrapper
    return decorate


def if_channel_like(regex: str) -> DecorateAsyncCallable:
    """
    Tests if the current channel matches the regular expression.
    """
    compiled_regex = re.compile(regex)

    def predicate(event: Event, **_: Any) -> bool:
        return bool(compiled_regex.fullmatch(event.channel))
    return if_(predicate)


def if_newer(callable_: AsyncCallable) -> AsyncCallable:
    """
    Tests if the event is newer than a previous one from the same channel.
    """
    def predicate(event: Event, previous: Optional[Event], **_: Any) -> bool:
        return previous is None or event.timestamp > previous.timestamp
    return if_(predicate)(callable_)


def if_changed(callable_: AsyncCallable) -> AsyncCallable:
    """
    Tests if the event value is different from the a previous one.
    """
    def predicate(event: Event, previous: Optional[Event], **_: Any) -> bool:
        return previous is None or event.value != previous.value
    return if_(predicate)(callable_)


def if_equals(value: Any) -> DecorateAsyncCallable:
    """
    Tests if event value equals to the specified one.
    """
    def predicate(event: Event, **_: Any) -> bool:
        return event.value == value
    return if_(predicate)


def if_not_equal(value: Any) -> DecorateAsyncCallable:
    """
    Tests if event value doesn't equal to the specified one.
    """
    def predicate(event: Event, **_: Any) -> bool:
        return event.value != value
    return if_(predicate)


def if_actual_value_equals(channel: str, value: Any) -> DecorateAsyncCallable:
    """
    Tests if an actual value equals to the specified one.
    """
    def predicate(actual: Mapping[str, Event], **_: Any) -> bool:
        event = actual.get(channel)
        return bool(event is not None and event.value == value)
    return if_(predicate)


def if_actual_value_not_equal(channel: str, value: Any) -> DecorateAsyncCallable:
    """
    Tests if an actual value doesn't equal to the specified one or is missing.
    """
    def predicate(actual: Mapping[str, Event], **_: Any) -> bool:
        event = actual.get(channel)
        return bool(event is None or event.value != value)
    return if_(predicate)


# Router singleton for a user's automation code.
router = EventRouter()
