from __future__ import annotations

import ssl
from typing import Any, Awaitable, Callable, Dict, Optional

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp_jinja2 import template
from loguru import logger
from pkg_resources import resource_string

from iftttie import templates
from iftttie.constants import ACTUAL_KEY
from iftttie.context import Context
from iftttie.decorators import authenticate_user
from iftttie.types_ import Event

routes = web.RouteTableDef()
statics = {
    name: resource_string('iftttie', f'static/{name}')
    for name in [
        'android-chrome-192x192.png',
        'android-chrome-512x512.png',
        'apple-touch-icon.png',
        'favicon.ico',
        'favicon-16x16.png',
        'favicon-32x32.png',
        'site.webmanifest',
    ]
}


def start(
    ssl_context: Optional[ssl.SSLContext],
    port: int,
    context: Context,
    on_startup: Callable[[web.Application], Awaitable[Any]],
    on_cleanup: Callable[[web.Application], Awaitable[Any]],
):
    """Start the web app."""
    app = web.Application()
    app['context'] = context
    # noinspection PyUnresolvedReferences
    app.on_startup.append(on_startup)
    # noinspection PyUnresolvedReferences
    app.on_cleanup.append(on_cleanup)
    app.add_routes(routes)

    templates.setup(app)

    logger.info('Using port {}.', port)
    # noinspection PyTypeChecker
    web.run_app(app, port=port, ssl_context=ssl_context, print=None)


@routes.get(r'/', name='index')
@template('index.html')
@authenticate_user
async def index(request: web.Request) -> dict:
    return {
        'actual': request.app['context'].get_actual().values(),
    }


@routes.get(r'/channel/{channel_id}', name='view')
@template('channel.html')
@authenticate_user
async def channel(request: web.Request) -> dict:
    try:
        event: Dict[Any, Any] = request.app['context'].db[ACTUAL_KEY][request.match_info['channel_id']]
    except KeyError:
        raise HTTPNotFound(text='Channel is not found.')
    return {'event': Event(**event), 'raw_event': event}


@routes.get(r'/{name:[^/]+}')
async def static(request: web.Request) -> web.Response:
    try:
        body = statics[request.match_info['name']]
    except KeyError:
        raise HTTPNotFound()
    else:
        return web.Response(body=body)


@routes.get(r'/downloads/db.sqlite3')
@authenticate_user
async def download_db(_: web.Request) -> web.FileResponse:
    return web.FileResponse('db.sqlite3', headers={'Content-Type': 'application/x-sqlite3'})
