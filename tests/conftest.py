from __future__ import annotations

from sqlite3 import Connection
from typing import Callable

from aiohttp.test_utils import TestClient
from pytest import fixture

from iftttie import templates, web
from iftttie.database import init_database
from iftttie.web import routes, Context

pytest_plugins = 'aiohttp.pytest_plugin'


@fixture
async def db() -> Connection:
    return init_database(':memory:')


@fixture
async def iftttie_client(aiohttp_client: Callable[..., TestClient], db: Connection) -> TestClient:
    # noinspection PyTypeChecker
    app = web.Application(Context(configuration_url='', users=[], db=db))
    app.add_routes(routes)
    templates.setup(app)
    return await aiohttp_client(app)
