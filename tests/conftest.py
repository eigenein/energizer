from __future__ import annotations

from sqlite3 import Connection
from typing import Callable

from aiohttp import web
from aiohttp.test_utils import TestClient
from pytest import fixture

from iftttie import templates
from iftttie.database import init_database
from iftttie.web import routes

pytest_plugins = 'aiohttp.pytest_plugin'


@fixture
async def db() -> Connection:
    return init_database(':memory:')


@fixture
async def iftttie_client(aiohttp_client: Callable[..., TestClient], db: Connection) -> TestClient:
    app = web.Application()
    app.add_routes(routes)
    templates.setup(app)
    app['db'] = db
    return await aiohttp_client(app)
