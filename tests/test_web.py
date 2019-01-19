from __future__ import annotations

from aiohttp.test_utils import TestClient


async def test_index(iftttie_client: TestClient):
    response = await iftttie_client.get('/')
    assert response.status == 200
