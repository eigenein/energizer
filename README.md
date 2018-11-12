## Settings

### `IFTTTIE_ACCESS_TOKEN`

The token used to access IFTTTie, choose any long random string.

### `IFTTTIE_IFTTT_TOKEN`

Obtain IFTTT Maker Webhooks here: https://ifttt.com/maker_webhooks.

### `IFTTTIE_NEST_TOKEN`

Obtain Nest API OAuth token here: https://developers.nest.com/guides/api/how-to-auth.

### `IFTTTIE_BUIENRADAR_STATION_ID`

Choose your station ID here: https://api.buienradar.nl/data/public/2.0/jsonfeed.

## Web

Dashboard is available at the root URL.

## API

### POST `/api/from/{channel_id}`

Submit a value coming _from_ the channel, so from a service or a device.

#### POST `/api/to/{channel_id}`

Submit a value _to_ the channel, so to a device.
