from __future__ import annotations

from aiohttp import BasicAuth
from aiohttp.test_utils import TestClient


async def test_index(iftttie_client: TestClient):
    response = await iftttie_client.get('/', auth=BasicAuth(
        login='test',
        password='1',
    ))
    assert response.status == 200


async def test_index_without_auth(iftttie_client: TestClient):
    response = await iftttie_client.get('/')
    assert response.status == 401


async def test_download_without_auth(iftttie_client: TestClient):
    response = await iftttie_client.get('/db.sqlite3')
    assert response.status == 401
