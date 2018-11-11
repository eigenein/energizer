from aiohttp import web

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request: web.Request) -> web.Response:
    return web.Response(text="Hello, world")


def run(http_port: int):
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=http_port, print=None)
