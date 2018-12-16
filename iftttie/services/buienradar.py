from __future__ import annotations

from asyncio import sleep
from typing import AsyncIterator

from aiohttp import ClientSession, web
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.services.base import BaseService

url = 'https://api.buienradar.nl/data/public/2.0/jsonfeed'
keys = (
    ('airpressure', 'air_pressure'),
    ('feeltemperature', 'feel_temperature'),
    ('groundtemperature', 'ground_temperature'),
    ('humidity', 'humidity'),
    ('temperature', 'temperature'),
    ('winddirection', 'wind_direction'),
    ('windspeed', 'windspeed'),
    ('windspeedBft', 'windspeed_bft'),
)


class Buienradar(BaseService):
    def __init__(self, station_id: int, interval=600.0):
        self.station_id = station_id
        self.interval = interval

    async def yield_updates(self, app: web.Application) -> AsyncIterator[Update]:
        session: ClientSession = app['client_session']
        while True:
            async with session.get(url) as response:  # type ClientResponse
                feed = await response.json()
            for measurement in feed['actual']['stationmeasurements']:
                if measurement['stationid'] == self.station_id:
                    for source_key, target_key in keys:
                        yield Update(key=f'buienradar:{self.station_id}:{target_key}', value=measurement[source_key])
                    break
            else:
                logger.error('Station {station_id} is not found.', station_id=self.station_id)
            await sleep(self.interval)
