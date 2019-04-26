from __future__ import annotations

from textwrap import dedent
from types import ModuleType
from typing import Callable

from aiohttp.test_utils import TestClient
from aiohttp.web import Application
from pytest import fixture
from sqlitemap import Connection

from my_iot import templates
from my_iot.imp_ import create_module
from my_iot.web import Context, routes

pytest_plugins = 'aiohttp.pytest_plugin'


@fixture
async def db() -> Connection:
    return Connection(':memory:')


@fixture
async def automation() -> ModuleType:
    return create_module(name='test_automation', source=dedent('''\
        USERS = [
            ('test', '$pbkdf2-sha256$29000$tPaeE.Kck5Ly/n/vnXOuFQ$2C/q3Fk/5MoX149flqyXow0CY/UCSt31Ga4xIZAWeEg'),
        ]
    '''))


@fixture
async def client(aiohttp_client: Callable[..., TestClient], automation: ModuleType, db: Connection) -> TestClient:
    app = Application()
    # noinspection PyTypeChecker
    app['context'] = Context(automation=automation, db=db)
    app.add_routes(routes)
    templates.setup(app)
    yield await aiohttp_client(app)
    await app['context'].close()
