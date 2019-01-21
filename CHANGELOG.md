### `latest`

- Fix: #3 fix `hash-password` output
- Fix: #3 adjust `PasswordHasher` parameters for Raspberry Pi Zero W
- Fix: catch `TimeoutError` in `Nest`
- Fix: #3 authenticate user for `/system/db.sqlite3` and `/view/{key}`
- Chore: change `/system/db.sqlite3` to `/db.sqlite3`

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

- **Charts in the detail views**
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
