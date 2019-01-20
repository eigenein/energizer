# IFFTTie

Yet another home automation service.

[![Build Status](https://travis-ci.com/eigenein/iftttie.svg?branch=master)](https://travis-ci.com/eigenein/iftttie)
![Python Versions](https://img.shields.io/pypi/pyversions/iftttie.svg)
![Version](https://img.shields.io/pypi/v/iftttie.svg)
![Docker Pulls](https://img.shields.io/docker/pulls/eigenein/iftttie.svg)
![License](https://img.shields.io/github/license/eigenein/iftttie.svg)

## Web interface

![IFTTTie screenshot](https://eigenein.github.io/iftttie/README.png)

## Why not [Home Assistant](https://www.home-assistant.io/) or [OpenHAB](https://www.openhab.org/)?

There're multiple reasons why I didn't like them:

- Quite heavy. Their restart or configuration update takes ages.
- I can't catch all those _things_, _entities_, _channels_ and etc and relations between them. I want something simpler.
- Too flexible. While this may be good, I'm getting tired configuring all those _things_.
- Custom automation syntax. This may be perfect for non-developers, but I prefer to write in [my favorite language](https://www.python.org/).
- Inconvenient configuration. It's stored inside a container, separate web interfaces are needed to edit it via browser.

## General idea

In IFFTTie there're only **two** terms to understand: *service* and *update*.

### What's a *service*?

*Service* is an interface to the outside world. It serves two goals:

- You control the outside world with its public methods.
- It generates *updates*.

#### Examples

- [Nest API](https://developers.nest.com/documentation/api-reference)
- [Buienradar](https://www.buienradar.nl/)
- [IFFTT](https://ifttt.com/maker_webhooks)

### What's an *update*?

The term stands for itself. Update contains information that something has changed in the world. An update consists of a *key* and a *value*. *Key* is a globally unique identifier which is used to refer to a particular *value* in the world.

#### Examples

| key                                  | value     |
| ------------------------------------ | --------- |
| `buienradar:6391:temperature`        | `2.8`     |
| `nest:camera:0123…9876:is_streaming` | `true`    |
| `webhook:hello`                      | `'world'` |

## Configuration

IFTTTie reads its configuration from a single file. And there're two important things:

- It's **non-local**. You pass a **URL** via command line parameter or environment variable. IFTTTie loads the file when (re-)started. Think here of a secret [Gist](https://gist.github.com/) URL, for example. **Never share your configuration publicly as soon as it contains any credentials.**
- It's a **Python module**. You can write any valid Python code in there. IFTTTie Python API is described further. **Don't blindly trust others' code.**

## Running

Web server listens to the port `8443`.

### Locally

```text
$ virtualenv -p python3.7 venv
$ source venv/bin/activate
$ pip install iftttie
$ iftttie --help
Usage: iftttie [OPTIONS]

  Yet another home automation service.

Options:
  -c, --config TEXT  Configuration URL.  [required]
  --cert FILE        Server certificate path.
  --key FILE         Server private key path.
  -v, --verbose      Logging verbosity.
  --help             Show this message and exit.
```

### Docker

```bash
docker run -it --rm eigenein/iftttie iftttie -vvv -c https://gist.githubusercontent.com/user/repo/raw
```

The image supports running on Raspberry Pi out-of-the-box. With useful flags:

```bash
docker volume create iftttie
docker run \
    --detach \
    --restart always \
    --name iftttie \
    -p 8443:8443 \
    -v iftttie:/app \
    -v /etc/letsencrypt/live/example.com/cert.pem:/app/cert.pem:ro \
    -v /etc/letsencrypt/live/example.com/privkey.pem:/app/privkey.pem:ro \
    -e TZ=Europe/Amsterdam
    eigenein/iftttie -vvv -c https://gist.githubusercontent.com/user/repo/raw --cert cert.pem --key privkey.pem
```

#### `docker-compose.yml`

```yaml
version: '3.7'
services:
  iftttie:
    image: eigenein/iftttie:latest
    ports:
    - '443:8443'
    volumes:
    - '/home/pi/iftttie.sqlite3:/app/db.sqlite3'
    - '/etc/letsencrypt/live/example.com/cert.pem:/app/cert.pem:ro'
    - '/etc/letsencrypt/live/example.com/privkey.pem:/app/privkey.pem:ro'
    environment:
      TZ: 'Europe/Amsterdam'
      IFTTTIE_VERBOSITY: '3'
      IFTTTIE_CONFIGURATION_URL: 'https://gist.githubusercontent.com/user/repo/raw'
      IFTTTIE_CERT_PATH: 'cert.pem'
      IFTTTIE_KEY_PATH: 'privkey.pem'
      IFTTTIE_USERS: '<login> <password-hash>'
```

## Startup

At its (re-)start, IFTTTie imports the configuration module. Then, it starts all services specified in `services` module attribute.

The following function from the imported module will be run for every update:

```python
from iftttie.dataclasses_ import Update


# Name must be `on_update`.
async def on_update(update: Update):
    ...
```

### Configuration example

```python
NEST_TOKEN = ...
BUIENRADAR_STATION_ID = ...
LIVING_ROOM_CAMERA_ID = ...

from datetime import timedelta

from iftttie.dataclasses_ import Update
from iftttie.services.buienradar import Buienradar
from iftttie.services.clock import Clock
from iftttie.services.nest import Nest

nest = Nest(NEST_TOKEN)
clock = Clock('hello', timedelta(seconds=1.0))
buienradar = Buienradar(BUIENRADAR_STATION_ID)

services = [nest, clock, buienradar]


async def on_update(update: Update):
    print(update)
```

## Recipes

This section aims to demonstrate different practical examples of IFTTTie configuration.

### Display names

If you add `display_name: Dict[str, str]` attribute to your configuration, it will be used to replace long and ugly identifiers in the web interface.

For instance:

```python
BUIENRADAR_STATION_ID = ...

display_name = {
    f'buienradar:{BUIENRADAR_STATION_ID}:humidity': 'Humidity',
}
```

## Python API

### `iftttie.dataclasses_.Update`

#### `key: str`

This is just update *key* that's described above.

#### `value: Any`

The related *value*. Very specific to a particular service.

#### `timestamp: datetime`

Time and date when the event has occurred.

#### `unit: Unit`

Specifies what this value is. For instance, `Unit.CELSIUS` or `Unit.BOOLEAN`.

### Service classes

#### `iftttie.services.clock.Clock`

Yields periodical events with the specified `key`. Value then increments by one from zero on every tick.

```python
from datetime import timedelta


def __init__(self, key: str, interval: timedelta):
    ...
```

##### Example configuration

```python
from datetime import timedelta

from iftttie.services.clock import Clock

clock = Clock('hello', timedelta(seconds=1.0))
```

##### Example output

```text
Nov 17 00:09:03 (iftttie.core:54) [D] Requesting updates from Clock(key='hello', interval=1.0)…
Nov 17 00:09:04 (iftttie.core:83) [S] clock:hello = 219
```

#### `iftttie.services.nest.Nest`

Yields events from your Nest structure.

```python
def __init__(self, token: str):
    ...
```

#### `iftttie.services.buienradar.Buienradar`

Yields weather information from Dutch [Buienradar](https://www.buienradar.nl/) service.

```python
from datetime import timedelta


def __init__(self, station_id: int, interval=timedelta(seconds=300.0)):
    ...
```

##### Example configuration

```python
from iftttie.services.buienradar import Buienradar

buienradar = Buienradar(6240)
```

##### Example output

```text
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:air_pressure = 1012.19
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:feel_temperature = -1.5
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:ground_temperature = 3.2
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:humidity = 97.0
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:temperature = 3.1
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:wind_direction = 'ZZO'
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:wind_speed = 5.87
Nov 17 00:18:02 (iftttie.core:83) [S] buienradar:6240:wind_speed_bft = 4
```

#### `iftttie.services.file_.File`

Periodically yields contents of the specified file.

```python
from datetime import timedelta
from pathlib import Path

from iftttie.enums import Unit


def __init__(self, path: Path, key: str, interval: timedelta, unit: Unit):
    ...
```

#### `iftttie.services.file_.FloatValueFile`

Periodically yields floating-point value from the specified file.

```python
from datetime import timedelta
from pathlib import Path

from iftttie.enums import Unit


def __init__(self, path: Path, key: str, interval: timedelta, unit: Unit, scale=1.0):
    ...
```

##### Example configuration

```python
from datetime import timedelta
from pathlib import Path

from iftttie.enums import Unit
from iftttie.services.file_ import FloatValueFile

cpu_temperature = FloatValueFile(
    Path('/sys/class/thermal/thermal_zone0/temp'), 
    'cpu_temperature', 
    timedelta(seconds=10.0),
    Unit.CELSIUS,
    0.001, 
)
```

## Public HTTP API

You can send custom updates to IFTTTie from outside via its public API.

TODO
