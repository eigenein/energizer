from __future__ import annotations

from typing import Callable

from aiohttp.test_utils import TestClient
from pytest import fixture
from sqlitemap import Connection

from iftttie import templates, web
from iftttie.web import Context, routes

pytest_plugins = 'aiohttp.pytest_plugin'


@fixture
async def db() -> Connection:
    return Connection(':memory:')


@fixture
async def iftttie_client(aiohttp_client: Callable[..., TestClient], db: Connection) -> TestClient:
    # noinspection PyTypeChecker
    app = web.Application(Context(
        setup=None,
        users=[('test', '$pbkdf2-sha256$29000$tPaeE.Kck5Ly/n/vnXOuFQ$2C/q3Fk/5MoX149flqyXow0CY/UCSt31Ga4xIZAWeEg')],
        db=db,
    ))
    app.add_routes(routes)
    templates.setup(app)
    return await aiohttp_client(app)
