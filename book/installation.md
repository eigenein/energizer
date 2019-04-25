# Running

## Locally

```text
$ virtualenv -p python3.7 venv
$ source venv/bin/activate
$ pip install myiot
$ myiot --help
Usage: myiot [OPTIONS]

  Yet another home automation service.

Options:
  -c, --config TEXT  Configuration URL.  [required]
  --cert FILE        Server certificate path.
  --key FILE         Server private key path.
  -v, --verbose      Logging verbosity.
  --help             Show this message and exit.
```

## Docker

The image supports running on Raspberry Pi out-of-the-box:

```bash
docker volume create myiot
docker run \
    --detach \
    --restart always \
    --name myiot \
    --net host \
    --sysctl net.ipv4.ip_unprivileged_port_start=0 \
    -v myiot:/app \
    -v /etc/letsencrypt/live/example.com/cert.pem:/app/cert.pem:ro \
    -v /etc/letsencrypt/live/example.com/privkey.pem:/app/privkey.pem:ro \
    -e TZ=Europe/Amsterdam
    eigenein/myiot -vvv -c https://gist.githubusercontent.com/user/repo/raw --cert cert.pem --key privkey.pem
```

### `docker-compose.yml`

```yaml
version: '3.7'
services:
  myiot:
    image: eigenein/myiot:latest
    restart: always
    network_mode: 'host'
    sysctls:
    - net.ipv4.ip_unprivileged_port_start=0
    volumes:
    - '/home/pi/myiot.sqlite3:/app/db.sqlite3'
    - '/etc/letsencrypt/live/example.com/cert.pem:/app/cert.pem:ro'
    - '/etc/letsencrypt/live/example.com/privkey.pem:/app/privkey.pem:ro'
    environment:
      TZ: 'Europe/Amsterdam'
      MYIOT_VERBOSITY: '3'
      MYIOT_CONFIGURATION_URL: 'https://gist.githubusercontent.com/user/repo/raw'
      MYIOT_CERT_PATH: 'cert.pem'
      MYIOT_KEY_PATH: 'privkey.pem'
      MYIOT_PORT: 443
```
