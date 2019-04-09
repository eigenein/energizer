from __future__ import annotations

from asyncio import sleep
from datetime import datetime, timedelta
from typing import Any

from aiohttp import ClientSession
from loguru import logger
from pytz import timezone

from iftttie.channels.base import BaseChannel
from iftttie.context import Context
from iftttie.types_ import Event, Unit

tz = timezone('Europe/Amsterdam')
url = 'https://api.buienradar.nl/data/public/2.0/jsonfeed'
headers = {'Cache-Control': 'no-cache'}
keys = (
    ('airpressure', 'air_pressure', Unit.HPA, 'Pressure'),
    ('feeltemperature', 'feel_temperature', Unit.CELSIUS, 'Feels Like'),
    ('groundtemperature', 'ground_temperature', Unit.CELSIUS, 'Ground Temperature'),
    ('humidity', 'humidity', Unit.RH, 'Humidity'),
    ('temperature', 'temperature', Unit.CELSIUS, 'Air Temperature'),
    ('winddirection', 'wind_direction', Unit.ENUM, 'Wind Direction'),
    ('windspeed', 'wind_speed', Unit.MPS, 'Wind Speed'),
    ('windspeedBft', 'wind_speed_bft', Unit.BEAUFORT, 'Wind BFT'),
    ('sunpower', 'sun_power', Unit.WATT, 'Sun Power'),
    ('weatherdescription', 'weather_description', Unit.TEXT, 'Description'),
)


class Buienradar(BaseChannel):
    def __init__(self, station_id: int, interval=timedelta(seconds=300.0)):
        self.station_id = station_id
        self.interval = interval.total_seconds()

    async def run(self, context: Context, **kwargs: Any):
        async with ClientSession(headers=headers) as session:
            while True:
                async with session.get(url, headers=headers) as response:
                    feed = await response.json()
                await self.trigger_events(context, feed)
                logger.debug('Next reading in {interval} seconds.', interval=self.interval)
                await sleep(self.interval)

    async def trigger_events(self, context: Context, feed: Any):
        if feed['actual']['sunrise']:
            sunrise = parse_datetime(feed['actual']['sunrise'])
            await context.trigger_event(Event(
                key='buienradar:sunrise',
                value=sunrise,
                unit=Unit.DATETIME,
                title='Sunrise',
            ))
        else:
            logger.warning('Sunrise time is missing.')
            sunrise = None
        if feed['actual']['sunset']:
            sunset = parse_datetime(feed['actual']['sunset'])
            await context.trigger_event(Event(
                key='buienradar:sunset',
                value=sunset,
                unit=Unit.DATETIME,
                title='Sunset',
            ))
        else:
            logger.warning('Sunset time is missing.')
            sunset = None
        if sunset and sunrise:
            await context.trigger_event(Event(
                key='buienradar:day_length',
                value=(sunset - sunrise),
                unit=Unit.TIMEDELTA,
                title='Day Length',
            ))
        try:
            measurement = self.find_measurement(feed)
        except KeyError as e:
            logger.error('Station ID {} is not found.', e)
            return
        for source_key, target_key, unit, title in keys:
            await context.trigger_event(Event(
                key=f'buienradar:{self.station_id}:{target_key}',
                value=measurement[source_key],
                unit=unit,
                timestamp=parse_datetime(measurement['timestamp']),
                title=f'{measurement["stationname"]} {title}',
            ))

    def find_measurement(self, feed: Any) -> Any:
        for measurement in feed['actual']['stationmeasurements']:
            if measurement['stationid'] == self.station_id:
                return measurement
        raise KeyError(self.station_id)

    def __str__(self) -> str:
        return f'{Buienradar.__name__}(station_id={self.station_id!r})'


def parse_datetime(value: str) -> float:
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S').astimezone(tz).timestamp()
