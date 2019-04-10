from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Tuple

from aiohttp.test_utils import TestClient
from pytest import fixture
from sqlitemap import Connection

from iftttie import templates, web
from iftttie.web import Context, routes

pytest_plugins = 'aiohttp.pytest_plugin'


@dataclass
class Setup:
    USERS: List[Tuple[str, str]]


@fixture
async def db() -> Connection:
    return Connection(':memory:')


@fixture
async def client(aiohttp_client: Callable[..., TestClient], db: Connection) -> TestClient:
    users = [('test', '$pbkdf2-sha256$29000$tPaeE.Kck5Ly/n/vnXOuFQ$2C/q3Fk/5MoX149flqyXow0CY/UCSt31Ga4xIZAWeEg')]
    app = web.Application(Context(setup=Setup(USERS=users), db=db))
    app.add_routes(routes)
    templates.setup(app)
    return await aiohttp_client(app)
