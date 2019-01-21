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
