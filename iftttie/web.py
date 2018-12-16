from __future__ import annotations

from datetime import datetime
from json import loads

import aiosqlite
import pkg_resources
from aiohttp import web
from aiohttp_jinja2 import template

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind

routes = web.RouteTableDef()
favicon_body = pkg_resources.resource_string('iftttie', 'static/favicon.png')


@routes.get('/')
@template('index.html')
async def index(request: web.Request) -> dict:
    db: aiosqlite.Connection = request.app['db']
    async with db.execute('''
        SELECT latest.key, value, timestamp, kind FROM latest
        JOIN history on latest.history_id = history.id
        ORDER BY latest.key
    ''') as cursor:  # type: aiosqlite.Cursor
        latest = [
            Update(key, loads(value), datetime.fromtimestamp(timestamp).astimezone(), ValueKind(kind))
            for key, value, timestamp, kind in await cursor.fetchall()
        ]
    return {'latest': latest}


@routes.get('/favicon.png')
async def favicon(_: web.Request) -> web.Response:
    return web.Response(body=favicon_body, content_type='image/png')
