# Recipes

## Monitor your Raspberry Pi CPU temperature

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

## If new Nest Cam event occurred, then send an animation to Telegram

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

## If Nest detects an intrusion, then send a message to Telegram

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
