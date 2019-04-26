from __future__ import annotations

from datetime import timedelta
from typing import Any, Awaitable, Callable, Dict

from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound
from aiohttp_jinja2 import template
from pkg_resources import resource_string

from my_iot import templates
from my_iot.constants import ACTUAL_KEY, HTTP_PORT
from my_iot.context import Context
from my_iot.types_ import Event

routes = web.RouteTableDef()
statics = {
    name: resource_string('my_iot', f'static/{name}')
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
    context: Context,
    on_startup: Callable[[web.Application], Awaitable[Any]],
    on_cleanup: Callable[[web.Application], Awaitable[Any]],
):
    """
    Start the web app.
    """
    app = web.Application()
    app['context'] = context
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    app.add_routes(routes)

    templates.setup(app)

    # noinspection PyTypeChecker
    web.run_app(app, port=HTTP_PORT, print=None)


@routes.get(r'/')
@template('index.html')
async def get_index(request: web.Request) -> dict:
    return {
        'actual': request.app['context'].get_actual().values(),
    }


@routes.get(r'/channel/{channel}')
@template('channel.html')
async def get_channel(request: web.Request) -> dict:
    context: Context = request.app['context']
    channel: str = request.match_info['channel']
    try:
        event: Dict[Any, Any] = context.db[ACTUAL_KEY][channel]
    except KeyError:
        raise HTTPNotFound(text='Channel is not found.')
    try:
        period = timedelta(seconds=max(int(request.query.get('period') or 300), 0))
    except ValueError:
        raise HTTPBadRequest()
    return {
        'event': Event(**event),
        'raw_event': event,
        'request': request,
        'events': context.get_log(channel, period),
    }


@routes.get(r'/downloads/db.sqlite3')
async def get_db(_: web.Request) -> web.FileResponse:
    return web.FileResponse('db.sqlite3', headers={'Content-Type': 'application/x-sqlite3'})


@routes.get(r'/events')
@template('events.html')
async def get_events(request: web.Request) -> dict:
    return {'request': request}


@routes.get(r'/services')
@template('services.html')
async def get_services(request: web.Request) -> dict:
    return {'services': request.app['context'].services}


# Must go at the end.
@routes.get(r'/{name:.+}')
async def get_static(request: web.Request) -> web.Response:
    try:
        body = statics[request.match_info['name']]
    except KeyError:
        raise HTTPNotFound()
    else:
        return web.Response(body=body)
