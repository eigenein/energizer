from __future__ import annotations

from asyncio import Queue, sleep
from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientSession
from loguru import logger

from iftttie.dataclasses_ import Update
from iftttie.enums import ValueKind
from iftttie.services.base import BaseService

url = 'https://api.buienradar.nl/data/public/2.0/jsonfeed'
headers=[('Cache-Control', 'no-cache')]
keys = (
    ('airpressure', 'air_pressure', ValueKind.HPA),
    ('feeltemperature', 'feel_temperature', ValueKind.CELSIUS),
    ('groundtemperature', 'ground_temperature', ValueKind.CELSIUS),
    ('humidity', 'humidity', ValueKind.HUMIDITY),
    ('temperature', 'temperature', ValueKind.CELSIUS),
    ('winddirection', 'wind_direction', ValueKind.OTHER),
    ('windspeed', 'wind_speed', ValueKind.MPS),
    ('windspeedBft', 'wind_speed_bft', ValueKind.BEAUFORT),
)
timestamp_format = '%Y-%m-%dT%H:%M:%S'


class Buienradar(BaseService):
    def __init__(self, station_id: int, interval=timedelta(seconds=300.0)):
        self.station_id = station_id
        self.interval = interval.total_seconds()

    async def run(self, client_session: ClientSession, event_queue: Queue[Update], **kwargs: Any):
        while True:
            async with client_session.get(url, headers=headers) as response:  # type ClientResponse
                feed = await response.json()
            for measurement in feed['actual']['stationmeasurements']:
                if measurement['stationid'] == self.station_id:
                    for source_key, target_key, kind in keys:
                        await event_queue.put(Update(
                            key=f'buienradar:{self.station_id}:{target_key}',
                            value=measurement[source_key],
                            kind=kind,
                            timestamp=datetime.strptime(measurement['timestamp'], timestamp_format).astimezone(),
                        ))
                    break
            else:
                logger.error('Station {station_id} is not found.', station_id=self.station_id)
            logger.debug('Next reading in {interval} seconds.', interval=self.interval)
            await sleep(self.interval)

    def __str__(self) -> str:
        return f'{Buienradar.__name__}(station_id={self.station_id!r})'
