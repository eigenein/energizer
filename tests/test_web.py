from __future__ import annotations

from aiohttp import test_utils
from aiohttp.web_response import Response
from pytest import mark


@mark.parametrize('url', [
    '/',
    '/favicon.ico',
    '/services',
    '/events',
])
async def test_url_200(client: test_utils.TestClient, url: str):
    response = await client.get(url)
    assert response.status == 200


@mark.parametrize('url', [
    '/__init__.py',
])
async def test_not_found(client: test_utils.TestClient, url: str):
    response = await client.get(url)
    assert response.status == 404


async def test_download(client: test_utils.TestClient):
    response: Response = await client.get('/downloads/db.sqlite3')
    assert response.status == 200
    assert response.content_type == 'application/x-sqlite3'
