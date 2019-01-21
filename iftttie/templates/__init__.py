from __future__ import annotations

import aiohttp_jinja2
from aiohttp.web_app import Application
from jinja2 import PackageLoader, select_autoescape

from iftttie.types import Unit


def setup(app: Application):
    env = aiohttp_jinja2.setup(app, loader=PackageLoader('iftttie'), autoescape=select_autoescape())
    env.globals['Unit'] = Unit
    env.filters['datetime'] = '{:%b %d %H:%M:%S}'.format
