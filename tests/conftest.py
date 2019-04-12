from __future__ import annotations

from typing import Callable

from aiohttp.test_utils import TestClient
from aiohttp.web import Application
from pytest import fixture
from sqlitemap import Connection

from iftttie import templates
from iftttie.automation import Automation
from iftttie.web import Context, routes

pytest_plugins = 'aiohttp.pytest_plugin'


@fixture
async def db() -> Connection:
    return Connection(':memory:')


@fixture
async def client(aiohttp_client: Callable[..., TestClient], db: Connection) -> TestClient:
    automation = Automation()
    automation.users.append(('test', '$pbkdf2-sha256$29000$tPaeE.Kck5Ly/n/vnXOuFQ$2C/q3Fk/5MoX149flqyXow0CY/UCSt31Ga4xIZAWeEg'))
    app = Application()
    app['context'] = Context(automation=automation, db=db)
    app.add_routes(routes)
    templates.setup(app)
    return await aiohttp_client(app)
