# Recipes

## Monitor your Raspberry Pi CPU temperature

```python
from datetime import timedelta
from pathlib import Path

from my_iot.services.file_ import FloatValueFile
from my_iot.types_ import Unit

SERVICES = [
    FloatValueFile(
        Path('/sys/class/thermal/thermal_zone0/temp'), 
        'cpu_temperature', 
        timedelta(seconds=5.0),
        Unit.CELSIUS,
        0.001,
        'CPU Temperature',
    ),
]
```

## If new Nest Cam event occurred, then send an animation to Telegram

```python
TELEGRAM_TOKEN = ...
TELEGRAM_CHAT_ID = ...
NEST_STRUCTURE_ID = ...
AWAY_CHANNEL = f'nest:structure:{NEST_STRUCTURE_ID}:away'

from typing import Any

from aiohttp import ClientSession

from my_iot.actions.telegram import ParseMode, send_animation
from my_iot.routing import (
    router,
    if_actual_value_not_equal,
    if_channel_like,
    if_newer,
)
from my_iot.types_ import Event


@router
@if_channel_like(r'.*:last_animated_image_url')
@if_newer
@if_actual_value_not_equal(AWAY_CHANNEL, 'home')
async def on_away_camera_event(*, event: Event, session: ClientSession, **_: Any):
    await send_animation(
        session=session,
        token=TELEGRAM_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        animation=event.value,
        disable_notification=True,
        caption=f'*{event.title}*\n{event.timestamp.astimezone():%b %d, %H:%M:%S}',
        parse_mode=ParseMode.MARKDOWN,
    )
```

## If Nest detects an intrusion, then send a message to Telegram

```python
TELEGRAM_TOKEN = ...
TELEGRAM_CHAT_ID = ...

from typing import Any

from aiohttp import ClientSession

from my_iot.actions.telegram import send_message
from my_iot.routing import (
    if_channel_like,
    if_changed,
    if_not_equal,
    router,
)


@router
@if_channel_like(r'.*:wwn_security_state')
@if_changed
@if_not_equal('ok')
async def on_deter(*, session: ClientSession, **_: Any):
    await send_message(
        session=session,
        token=TELEGRAM_TOKEN,
        chat_id=TELEGRAM_CHAT_ID,
        text='🔴 Intrusion detected',
    )
```
