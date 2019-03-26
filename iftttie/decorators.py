from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from aiohttp import BasicAuth, hdrs
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_request import Request
from loguru import logger
from passlib.handlers.pbkdf2 import pbkdf2_sha256

T = TypeVar('T')
THandler = Callable[[Request], Awaitable[T]]


def authenticate_user(handler: THandler[T]):
    headers = [('WWW-Authenticate', 'Basic realm="IFTTTie"')]

    @wraps(handler)
    async def wrapper(request: Request) -> T:
        logger.debug('Authenticating request…')

        header = request.headers.get(hdrs.AUTHORIZATION)
        if not header:
            raise HTTPUnauthorized(text='Welcome to IFTTTie! Please authenticate', headers=headers)

        try:
            auth = BasicAuth.decode(auth_header=header)
        except ValueError:
            raise HTTPUnauthorized(text='Invalid authorization header', headers=headers)

        for login, hash_ in request.app.context.users:
            if login != auth.login:
                continue
            if pbkdf2_sha256.verify(auth.password, hash_):
                logger.info('Authenticated user: {}', login)
                return await handler(request)

        raise HTTPUnauthorized(text='Invalid password. Please try again', headers=headers)

    return wrapper
