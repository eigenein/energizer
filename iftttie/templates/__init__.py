from __future__ import annotations

from datetime import datetime, timedelta

import aiohttp_jinja2
import pprintpp
from aiohttp.web_app import Application
from jinja2 import PackageLoader, select_autoescape

from iftttie.types_ import Unit


def setup(app: Application):
    env = aiohttp_jinja2.setup(app, loader=PackageLoader('iftttie'), autoescape=select_autoescape())
    env.globals['Unit'] = Unit
    env.filters['fromseconds'] = from_seconds
    env.filters['fromtimestamp'] = from_timestamp
    env.filters['pprint'] = pprintpp.pformat


def from_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime('%b %d, %H:%M:%S')


def from_seconds(seconds: float) -> str:
    return str(timedelta(seconds=seconds))  # TODO: improve.
