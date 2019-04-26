from __future__ import annotations

from aiohttp import BasicAuth, test_utils
from aiohttp.web_response import Response
from pytest import mark

auth = BasicAuth(login='test', password='1')


@mark.parametrize('url', [
    '/',
    '/favicon.ico',
    '/services',
    '/events',
])
async def test_with_auth(client: test_utils.TestClient, url: str):
    response = await client.get(url, auth=auth)
    assert response.status == 200


@mark.parametrize('url', [
    '/',
    '/downloads/db.sqlite3',
])
async def test_without_auth(client: test_utils.TestClient, url: str):
    response = await client.get(url)
    assert response.status == 401


@mark.parametrize('url', [
    '/__init__.py',
])
async def test_not_found(client: test_utils.TestClient, url: str):
    response = await client.get(url)
    assert response.status == 404


async def test_download(client: test_utils.TestClient):
    response: Response = await client.get('/downloads/db.sqlite3', auth=auth)
    assert response.status == 200
    assert response.content_type == 'application/x-sqlite3'
