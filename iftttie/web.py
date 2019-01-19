from __future__ import annotations

from sqlite3 import Connection

import pkg_resources
from aiohttp import web
from aiohttp_jinja2 import template

from iftttie.database import select_latest

routes = web.RouteTableDef()
favicon_body = pkg_resources.resource_string('iftttie', 'static/favicon.png')


@routes.get('/', name='index')
@template('index.html')
async def index(request: web.Request) -> dict:
    db: Connection = request.app['db']

    updates = select_latest(db)
    return {
        'updates': updates,
    }


@routes.get('/view/{key}', name='view')
@template('view.html')
async def view(request: web.Request) -> dict:
    # TODO: db: aiosqlite.Connection = request.app['db']
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


@routes.get('/system/db.sqlite3')
async def download(_: web.Request) -> web.Response:
    return web.FileResponse('db.sqlite3')
