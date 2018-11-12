from __future__ import annotations

from typing import Callable, Optional

from aiohttp import web

THandler = Callable[[web.Request], web.Response]


@web.middleware
async def authenticate(request: web.Request, handler: THandler) -> web.Response:
    token: Optional[str] = request.headers.get('Token') or request.query.get('token')
    if not token or token not in request.app['access_tokens']:
        raise web.HTTPUnauthorized(text='invalid token')
    return await handler(request)
