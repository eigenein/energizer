from __future__ import annotations

from functools import wraps
from typing import Awaitable, Callable, TypeVar

from aiohttp import BasicAuth, hdrs
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp.web_request import Request
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

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
            password = BasicAuth.decode(auth_header=header).password
        except ValueError:
            raise HTTPUnauthorized(text='Invalid authorization header', headers=headers)

        for hash_ in request.app['user_auth']:
            try:
                hasher.verify(hash_, password)
            except VerifyMismatchError:
                pass
            else:
                return await handler(request)

        raise HTTPUnauthorized(text='Invalid password. Please try again', headers=headers)

    return wrapper
