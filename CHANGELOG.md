## `master`

- **Change: #55 switch to a local setup instead of a configuration URL**
- **Change: #53 migrate to `sqlitemap`. This will invalidate all the existing data in the database**
- **Change: #51 use MessagePack for the database serialization**
- Change: brush up the navigation bar
- Fix: not having `pytest` in `dev` extras
- Fix: display timestamp timezone
- Fix: add comma to the datetime format
- Fix: add datetime hint to the channel page
- Opt: upgrade `pip` in `Dockerfile`
- Opt: upgrade `aiohttp`
- Chore: brush up `Makefile`
- Chore: #11 split up `README.md` into sections
- Chore: simplify code and prepare for future changes

## `0.9.0`

- Fix: #35 error logging in the `Nest` channel
- Chore: Add `publish/docker/latest` and `publish/docker/tag` make targets
- New: #34 Add Buienradar weather description
- New: #28 Prepare `Dockerfile` and `setup.py` for the `Ping` channel
- Fix: #35 Remove timeout for the `Nest` channel
- Opt: #37 Use a separate session for `Buienradar`
- Opt: #37 Get rid of the global `ClientSession` instance
- New: #23 Add Telegram `send_message` method
- Opt: upgrade `aiodns`
- Change: use `passlib` instead of `argon2-cffi`

## `0.8`

- Feat: #13 pass old value and all the current values to `on_event`
- Feat: #14 `send_animation` method for Telegram bots
- Chore: add `ipython` to the Docker image
- Chore: upgrade `loguru`
- Feat: set network capabilities for Python binary
- Change: move users to the configuration module
- Feat: specify port via command-line option or environment variable
- Feat: #31 asynchronous `on_event`
- Feat: #7 channel page

## `0.7`

- Fix: #3 fix `hash-password` output
- Fix: #3 adjust `PasswordHasher` parameters for Raspberry Pi Zero W
- Fix: catch `TimeoutError` in `Nest`
- Fix: #3 authenticate user for `/system/db.sqlite3` and `/view/{key}`
- Chore: change `/system/db.sqlite3` to `/db.sqlite3`
- Chore: subclass `web.Application` and provide `Context` class
- Chore: get rid of the event queue, call `on_update` directly
- Chore: #15 rename to channels and events

## `0.6`

- Feat: #3 user authentication with login

## `0.5`

- Feat: user authentication
- Chore: add `dev` install extra
- Chore: enable `pytest` in Travis

## `0.4`

- Fix: `id_` for `File` and `Clock`
- Opt: set `PYTHONOPTIMIZE=2` for the Python interpreter
- New: #10 set up unit testing and get rid of `aiosqlite` for now
- New: #9 database schema migrations

## `0.3`

- New: charts in the detail views
- Fix: passing options via environment variables
- Change: always start on port `8443`
- Opt: use [`aiohttp-sse-client`](https://pypi.org/project/aiohttp-sse-client/)
- Change: #2 #4 #6 Change database schema, rename `ValueKind` and add titles
- Chore: #4 refine `Unit` class
- Chore: #5 #6 denormalise database and add update IDs

## `0.2`

- Opt: improve `Dockerfile` and `Makefile`
- Opt: improve `Nest` and `Buienradar`
- Chore: move text constants to templates
- New: introduce new value kinds
- New: add SSL support
- New: detail view page
- Change: use `pickle` instead of JSON to store values in the database

## `0.1`

- New: initial release
