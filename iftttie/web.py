from __future__ import annotations

import ssl
from typing import Any, Awaitable, Callable, Optional

import pkg_resources
from aiohttp import web
from aiohttp_jinja2 import template

from iftttie import templates
from iftttie.context import Context
from iftttie.database import select_latest
from iftttie.decorators import authenticate_user

routes = web.RouteTableDef()
favicon_body = pkg_resources.resource_string('iftttie', 'static/favicon.png')


class Application(web.Application):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context


def start(
    ssl_context: Optional[ssl.SSLContext],
    context: Context,
    on_startup: Callable[[Application], Awaitable[Any]],
    on_cleanup: Callable[[Application], Awaitable[Any]],
):
    """Start the web app."""
    app = Application(context)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.add_routes(routes)

    templates.setup(app)

    web.run_app(app, port=8443, ssl_context=ssl_context, print=None)


@routes.get('/', name='index')
@template('index.html')
@authenticate_user
async def index(request: web.Request) -> dict:
    events = select_latest(request.app.context.db)
    return {
        'events': events,
    }


@routes.get('/view/{key}', name='view')
@template('view.html')
@authenticate_user
async def view(request: web.Request) -> dict:
    # TODO: key: str = request.match_info['key']

    raise NotImplementedError()


@routes.get('/favicon.png')
async def favicon(_: web.Request) -> web.Response:
    return web.Response(body=favicon_body, content_type='image/png')


@routes.get('/manifest.json')
async def manifest(_: web.Request) -> web.Response:
    return web.json_response({
        'short_name': 'IFTTTie',
        'name': 'IFTTTie',
        'icons': [{'src': '/favicon.png', 'type': 'image/png', 'sizes': '32x32'}],
        'start_url': '/',
        'background_color': '#000000',
        'display': 'standalone',
        'scope': '/',
        'theme_color': '#209cee',
    })


@routes.get('/db.sqlite3')
@authenticate_user
async def download_db(_: web.Request) -> web.Response:
    return web.FileResponse('db.sqlite3')
