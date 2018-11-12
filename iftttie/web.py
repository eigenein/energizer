from __future__ import annotations

from typing import Set

from aiohttp import web

from iftttie.middleware import authenticate

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request: web.Request) -> web.Response:
    return web.Response(text="Hello, world")


def run(http_port: int, access_tokens: Set[str]):
    app = web.Application(middlewares=[authenticate])
    app.add_routes(routes)
    app['access_tokens'] = access_tokens
    web.run_app(app, port=http_port, print=None)
