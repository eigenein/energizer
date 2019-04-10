from __future__ import annotations

from aiohttp import BasicAuth, test_utils
from aiohttp.web_response import Response

auth = BasicAuth(login='test', password='1')


async def test_favicon(client: test_utils.TestClient):
    response = await client.get('/favicon.ico')
    assert response.status == 200


async def test_not_found(client: test_utils.TestClient):
    response = await client.get('/__init__.py')
    assert response.status == 404


async def test_index(client: test_utils.TestClient):
    response = await client.get('/', auth=auth)
    assert response.status == 200


async def test_index_without_auth(client: test_utils.TestClient):
    response = await client.get('/')
    assert response.status == 401


async def test_download(client: test_utils.TestClient):
    response: Response = await client.get('/downloads/db.sqlite3', auth=auth)
    assert response.status == 200
    assert response.content_type == 'application/x-sqlite3'


async def test_download_without_auth(client: test_utils.TestClient):
    response = await client.get('/downloads/db.sqlite3')
    assert response.status == 401


# TODO: test channel page.
