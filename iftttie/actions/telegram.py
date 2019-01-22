from __future__ import annotations

from enum import Enum
from typing import Optional

from aiohttp import ClientResponse, ClientSession
from loguru import logger

url = 'https://api.telegram.org/bot{token}/{method}'


class ParseMode(str, Enum):
    MARKDOWN = 'Markdown'
    HTML = 'HTML'


async def send_animation(
    session: ClientSession,
    token: str,
    chat_id: str,
    animation: str,
    caption: Optional[str] = None,
    parse_mode: Optional[ParseMode] = None,
    disable_notification: bool = False,
) -> ClientResponse:
    data = {
        'chat_id': chat_id,
        'animation': animation,
        'disable_notification': disable_notification,
    }
    if caption:
        data['caption'] = caption
    if parse_mode:
        data['parse_mode'] = parse_mode.value
    logger.trace('send_animation(animation={!r})', animation)
    return await session.post(url.format(token=token, method='sendAnimation'), data=data)
