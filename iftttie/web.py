from __future__ import annotations

from datetime import datetime
from typing import Dict

import aiosqlite
import pkg_resources
from aiohttp import web
from aiohttp_jinja2 import template
from ujson import loads

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind

routes = web.RouteTableDef()
favicon_body = pkg_resources.resource_string('iftttie', 'static/favicon.png')


@routes.get('/')
@template('index.html')
async def index(request: web.Request) -> dict:
    db: aiosqlite.Connection = request.app['db']
    display_names: Dict[str, str] = request.app['display_names']

    async with db.execute('''
        SELECT latest.key, value, latest.timestamp, kind FROM latest
        JOIN history on latest.key = history.key AND latest.timestamp = history.timestamp
        ORDER BY latest.kind, latest.key
    ''') as cursor:  # type: aiosqlite.Cursor
        updates = [
            Update(key, loads(value), datetime.fromtimestamp(timestamp / 1000).astimezone(), ValueKind(kind))
            for key, value, timestamp, kind in await cursor.fetchall()
        ]
    return {
        'with_names': [update for update in updates if update.key in display_names],
        'without_names': [update for update in updates if update.key not in display_names],
    }


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
