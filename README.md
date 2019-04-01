# IFFTTie

Yet another home automation service.

[![Build Status](https://travis-ci.com/eigenein/iftttie.svg?branch=master)](https://travis-ci.com/eigenein/iftttie)
[![Python Versions](https://img.shields.io/pypi/pyversions/iftttie.svg)](https://pypi.org/project/iftttie/)
[![Version](https://img.shields.io/pypi/v/iftttie.svg)](https://pypi.org/project/iftttie/)
![Docker Pulls](https://img.shields.io/docker/pulls/eigenein/iftttie.svg)
![License](https://img.shields.io/github/license/eigenein/iftttie.svg)
[![Open issues](https://img.shields.io/github/issues-raw/eigenein/iftttie.svg)](https://github.com/eigenein/iftttie/issues)
[![Closed issues](https://img.shields.io/github/issues-closed-raw/eigenein/iftttie.svg)](https://github.com/eigenein/iftttie/issues)

## Web interface

![IFTTTie screenshot](https://eigenein.github.io/iftttie/README.png)

## Why not [Home Assistant](https://www.home-assistant.io/) or [OpenHAB](https://www.openhab.org/)?

There're multiple reasons why I didn't like them:

- Quite heavy. Their restart or configuration update takes ages.
- I can't catch all those _things_, _entities_, _channels_ and etc and relations between them. I want something simpler.
- Too flexible. While this may be good, I'm getting tired configuring all those _things_.
- Custom automation syntax. This may be perfect for non-developers, but I prefer to write in [my favorite language](https://www.python.org/).
- Inconvenient configuration. It's stored inside a container, separate web interfaces are needed to edit it via browser.

## Configuration

IFTTTie reads its configuration from a single Python file. And there're two important things to know about it:

- It's **non-local**. You pass an **URL** via the command line option or the environment variable. IFTTTie loads the file when (re-)started. Think here of a secret [Gist](https://gist.github.com/) URL, for example. **Never share your configuration publicly as soon as it contains any credentials.**
- You can write any valid Python code in there. **Don't blindly trust others' code.**

## Running

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

The image supports running on Raspberry Pi out-of-the-box:

```bash
docker volume create iftttie
docker run \
    --detach \
    --restart always \
    --name iftttie \
    --net host \
    --sysctl net.ipv4.ip_unprivileged_port_start=0 \
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
    restart: always
    network_mode: 'host'
    sysctls:
    - net.ipv4.ip_unprivileged_port_start=0
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
      IFTTTIE_PORT: 443
```

## Recipes

Since the projects lacks a good documentation, here're some specific examples of automation.

### Monitor your Raspberry Pi CPU temperature

```python
from datetime import timedelta
from pathlib import Path

from iftttie.channels.file_ import FloatValueFile
from iftttie.types import Unit

channels = [
    FloatValueFile(
        Path('/sys/class/thermal/thermal_zone0/temp'), 
        'cpu_temperature', 
        timedelta(seconds=10.0),
        Unit.CELSIUS,
        0.001,
        'CPU Temperature',
    ),
]
```

### If new Nest Cam event occurred, then send an animation to Telegram

```python
TELEGRAM_TOKEN = ...
TELEGRAM_CHAT_ID = ...

from typing import Any, Dict, Optional

from aiohttp import ClientSession

from iftttie.actions.telegram import send_animation
from iftttie.types import Event

session = ClientSession()


async def on_event(*, event: Event, old_event: Optional[Event], latest_events: Dict[str, Event], **kwargs: Any):
    if event.key.endswith(':last_animated_image_url') and (old_event is None or event.timestamp > old_event.timestamp):
        await send_animation(
            session=session, 
            token=TELEGRAM_TOKEN, 
            chat_id=TELEGRAM_CHAT_ID, 
            animation=event.value,
            disable_notification=True,
            caption=event.title,
        )


async def on_close():
    await session.close()
```

### If Nest detects an intrusion, then send a message to Telegram

```python
TELEGRAM_TOKEN = ...
TELEGRAM_CHAT_ID = ...

from typing import Any, Dict, Optional

from aiohttp import ClientSession

from iftttie.actions.telegram import send_message
from iftttie.types import Event

session = ClientSession()


async def on_event(*, event: Event, old_event: Optional[Event], latest_events: Dict[str, Event], **kwargs: Any):
    if event.key.endswith(':wwn_security_state') and (old_event is None or event.value != old_event.value):
        await send_message(
            session=session,
            token=TELEGRAM_TOKEN,
            chat_id=TELEGRAM_CHAT_ID,
            text=('🚨 Intrusion detected' if event.value != 'ok' else '✅ Security state is okay'),
        )


async def on_close():
    await session.close()
```
