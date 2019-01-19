### `latest`

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
