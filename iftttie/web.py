from __future__ import annotations

from aiohttp import web
from aiohttp_jinja2 import template

routes = web.RouteTableDef()


@routes.get('/')
@template('index.html')
async def index(request: web.Request) -> dict:
    return {}
