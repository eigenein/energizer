from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from aiohttp import BasicAuth, hdrs
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_request import Request
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from loguru import logger

T = TypeVar('T')
THandler = Callable[[Request], Awaitable[T]]


def authenticate_user(handler: THandler[T]):
    hasher = PasswordHasher()
    headers = [('WWW-Authenticate', 'Basic realm="IFTTTie"')]

    @wraps(handler)
    async def wrapper(request: Request) -> T:
        header = request.headers.get(hdrs.AUTHORIZATION)
        if not header:
            raise HTTPUnauthorized(text='Welcome to IFTTTie! Please authenticate', headers=headers)

        try:
            auth = BasicAuth.decode(auth_header=header)
        except ValueError:
            raise HTTPUnauthorized(text='Invalid authorization header', headers=headers)

        for login, hash_ in request.app['users']:
            if login != auth.login:
                continue
            try:
                hasher.verify(hash_, auth.password)
            except VerifyMismatchError:
                pass
            else:
                logger.info('User: {}', login)
                return await handler(request)

        raise HTTPUnauthorized(text='Invalid password. Please try again', headers=headers)

    return wrapper
