from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from aiohttp import ClientResponse, ClientSession
from loguru import logger

url = 'https://api.telegram.org/bot{token}/{method}'


class ParseMode(str, Enum):
    MARKDOWN = 'Markdown'
    HTML = 'HTML'


async def post(session: ClientSession, token: str, method: str, data: Dict[Any, Any]) -> ClientResponse:
    logger.info('{}', method)
    response: ClientResponse = await session.post(url.format(token=token, method=method), data=data)
    if response.status != 200:
        logger.error('Telegram error: {}', await response.text())
    return response


async def send_message(
    session: ClientSession,
    token: str,
    chat_id: str,
    text: str,
    parse_mode: Optional[ParseMode] = None,
    disable_web_page_preview: bool = False,
    disable_notification: bool = False,
):
    data = {
        'chat_id': chat_id,
        'text': text,
        'disable_web_page_preview': disable_web_page_preview,
        'disable_notification': disable_notification,
    }
    if parse_mode:
        data['parse_mode'] = parse_mode.value
    logger.debug('send_message(text={!r})', text)
    return await post(session, token, 'sendMessage', data)


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
    logger.debug('send_animation(animation={!r})', animation)
    return await post(session, token, 'sendAnimation', data)
