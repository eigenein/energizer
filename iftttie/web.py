from __future__ import annotations

import ssl
from typing import Any, Awaitable, Callable, Optional

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp_jinja2 import template
from loguru import logger
from pkg_resources import resource_listdir, resource_string

from iftttie import templates
from iftttie.constants import ACTUAL_KEY
from iftttie.context import Context
from iftttie.decorators import authenticate_user

routes = web.RouteTableDef()
statics = {name: resource_string('iftttie', f'static/{name}') for name in resource_listdir('iftttie', 'static')}


class Application(web.Application):
    def __init__(self, context: Context):
        super().__init__()
        self.context = context


def start(
    ssl_context: Optional[ssl.SSLContext],
    port: int,
    context: Context,
    on_startup: Callable[[Application], Awaitable[Any]],
    on_cleanup: Callable[[Application], Awaitable[Any]],
):
    """Start the web app."""
    app = Application(context)
    # noinspection PyUnresolvedReferences
    app.on_startup.append(on_startup)
    # noinspection PyUnresolvedReferences
    app.on_cleanup.append(on_cleanup)
    app.add_routes(routes)

    templates.setup(app)

    logger.info('Using port {}.', port)
    web.run_app(app, port=port, ssl_context=ssl_context, print=None)


@routes.get('/', name='index')
@template('index.html')
@authenticate_user
async def index(request: web.Request) -> dict:
    return {
        'actual': request.app.context.get_actual().values(),
    }


@routes.get('/channel/{key}', name='view')
@template('channel.html')
@authenticate_user
async def channel(request: web.Request) -> dict:
    try:
        event = request.app.context.db[ACTUAL_KEY][request.match_info['key']]
    except KeyError:
        raise HTTPNotFound(text='Channel is not found.')
    return {'event': event}


@routes.get('/{name:.+(.png|.ico|.webmanifest)}')
async def static(request: web.Request) -> web.Response:
    return web.Response(body=statics[request.match_info['name']])


@routes.get('/db.sqlite3')
@authenticate_user
async def download_db(_: web.Request) -> web.FileResponse:
    return web.FileResponse('db.sqlite3')
