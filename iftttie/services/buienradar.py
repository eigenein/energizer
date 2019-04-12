from __future__ import annotations

from asyncio import sleep
from datetime import datetime, timedelta
from typing import Any, Iterable

from aiohttp import ClientSession
from loguru import logger
from pytz import timezone

from iftttie.services.base import Service
from iftttie.types_ import Event, Unit

tz = timezone('Europe/Amsterdam')
url = 'https://api.buienradar.nl/data/public/2.0/jsonfeed'
headers = {'Cache-Control': 'no-cache'}
channels = (
    ('airpressure', 'air_pressure', Unit.HPA, 'Pressure'),
    ('feeltemperature', 'feel_temperature', Unit.CELSIUS, 'Feels Like'),
    ('groundtemperature', 'ground_temperature', Unit.CELSIUS, 'Ground Temperature'),
    ('humidity', 'humidity', Unit.RH, 'Humidity'),
    ('temperature', 'temperature', Unit.CELSIUS, 'Air Temperature'),
    ('winddirection', 'wind_direction', Unit.ENUM, 'Wind Direction'),  # FIXME: translate to English.
    ('windspeed', 'wind_speed', Unit.MPS, 'Wind Speed'),
    ('windspeedBft', 'wind_speed_bft', Unit.BEAUFORT, 'Wind BFT'),
    ('sunpower', 'sun_power', Unit.WATT, 'Sun Power'),
    ('weatherdescription', 'weather_description', Unit.TEXT, 'Description'),
)


class Buienradar(Service):
    def __init__(self, station_id: int, interval=timedelta(seconds=300.0)):
        self.station_id = station_id
        self.interval = interval.total_seconds()

    @property
    async def events(self):
        async with ClientSession(headers=headers) as session:
            while True:
                async with session.get(url, headers=headers) as response:
                    # FIXME: use `pydantic` for the feed.
                    feed = await response.json()
                for event in self.yield_events(feed):
                    yield event
                logger.debug('Next reading in {interval} seconds.', interval=self.interval)
                await sleep(self.interval)

    def yield_events(self, feed: Any) -> Iterable[Event]:
        if feed['actual']['sunrise']:
            sunrise = parse_datetime(feed['actual']['sunrise'])
            yield Event(
                channel_id='buienradar:sunrise',
                value=sunrise,
                unit=Unit.DATETIME,
                title='Sunrise',
            )
        else:
            logger.warning('Sunrise time is missing.')
            sunrise = None
        if feed['actual']['sunset']:
            sunset = parse_datetime(feed['actual']['sunset'])
            yield Event(
                channel_id='buienradar:sunset',
                value=sunset,
                unit=Unit.DATETIME,
                title='Sunset',
            )
        else:
            logger.warning('Sunset time is missing.')
            sunset = None
        if sunset and sunrise:
            yield Event(
                channel_id='buienradar:day_length',
                value=(sunset - sunrise),
                unit=Unit.TIMEDELTA,
                title='Day Length',
            )
        try:
            measurement = self.find_measurement(feed)
        except KeyError as e:
            logger.error('Station ID {} is not found.', e)
            return
        timestamp = parse_datetime(measurement['timestamp'])
        for key, channel_id, unit, title in channels:
            yield Event(
                channel_id=f'buienradar:{self.station_id}:{channel_id}',
                value=measurement[key],
                unit=unit,
                timestamp=timestamp,
                title=f'{measurement["stationname"]} {title}',
            )

    def find_measurement(self, feed: Any) -> Any:
        for measurement in feed['actual']['stationmeasurements']:
            if measurement['stationid'] == self.station_id:
                return measurement
        raise KeyError(self.station_id)

    def __str__(self) -> str:
        return f'{Buienradar.__name__}(station_id={self.station_id!r})'


def parse_datetime(value: str) -> float:
    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S').astimezone(tz).timestamp()
