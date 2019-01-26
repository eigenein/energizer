### `latest`

- #35 Fix error logging in the `Nest` channel
- Add `publish/docker/latest` and `publish/docker/tag` make targets
- #34 Add Buienradar weather description
- #28 Prepare `Dockerfile` and `setup.py` for the `Ping` channel
- #35 Continue troubleshooting the `Nest` channel
- #35 Set connection timeout to 10 minutes

### `0.8`

- Feat: #13 pass old value and all the current values to `on_event`
- Feat: #14 `send_animation` method for Telegram bots
- Chore: add `ipython` to the Docker image
- Chore: upgrade `loguru`
- Feat: set network capabilities for Python binary
- Change: move users to the configuration module
- Feat: specify port via command-line option or environment variable
- Feat: #31 asynchronous `on_event`
- Feat: #7 channel page

### `0.7`

- Fix: #3 fix `hash-password` output
- Fix: #3 adjust `PasswordHasher` parameters for Raspberry Pi Zero W
- Fix: catch `TimeoutError` in `Nest`
- Fix: #3 authenticate user for `/system/db.sqlite3` and `/view/{key}`
- Chore: change `/system/db.sqlite3` to `/db.sqlite3`
- Chore: subclass `web.Application` and provide `Context` class
- Chore: get rid of the event queue, call `on_update` directly
- Chore: #15 rename to channels and events

### `0.6`

- Feat: #3 user authentication with login

### `0.5`

- Feat: user authentication
- Chore: add `dev` install extra
- Chore: enable `pytest` in Travis

### `0.4`

- Fix `id_` for `File` and `Clock`
- feat: set `PYTHONOPTIMIZE=2` for the Python interpreter
- feat: #10 set up unit testing and get rid of `aiosqlite` for now
- feat: #9 database schema migrations

### `0.3`

- Charts in the detail views
- Fix passing options via environment variables
- Always start on port `8443`
- Use [`aiohttp-sse-client`](https://pypi.org/project/aiohttp-sse-client/)
- #2 #4 #6 Change database schema, rename `ValueKind` and add titles
- Close #4: refine `Unit` class
- Close #5 #6: denormalise database and add update IDs

### `0.2`

- Improve `Dockerfile` and `Makefile`
- Improve `Nest` and `Buienradar`
- Move text constants to templates
- Introduce new value kinds
- Add SSL support
- Detail view page
- Use `pickle` instead of JSON to store values in the database

### `0.1`

Initial release.
