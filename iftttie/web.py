from __future__ import annotations

import pkg_resources
from aiohttp import web
from aiohttp_jinja2 import template

routes = web.RouteTableDef()
favicon_body = pkg_resources.resource_string('iftttie', 'static/favicon.png')


@routes.get('/')
@template('index.html')
async def index(request: web.Request) -> dict:
    return {}


@routes.get('/favicon.png')
async def favicon(_: web.Request) -> web.Response:
    return web.Response(body=favicon_body, content_type='image/svg+xml')
