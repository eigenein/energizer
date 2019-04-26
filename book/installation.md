# Installation

My IoT is developed as a normal Python package and thus could be run via the console entry point. This is what you would do to develop it. But for production deployment it is recommended to use [Docker Compose](https://docs.docker.com/compose/). Then Docker becomes the only pre-requisite.

## HTTPS

Set up [Let's Encrypt](https://letsencrypt.org/). That is out of scope for this tutorial.

## `nginx.conf`

You'll need an Nginx reverse proxy configuration. Don't worry, just copy-paste the following one and change paths in `ssl_certificate` and `ssl_certificate_key`:

```nginx
http {
    upstream backend {
        server localhost:8080;
        keepalive 32;
    }

    server {
        listen 443 ssl default_server;
        listen [::]:443 default_server;
        charset utf-8;
        
        add_header Strict-Transport-Security max-age=2592000;
        
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_protocols  TLSv1 TLSv1.1 TLSv1.2;
        ssl_certificate /etc/letsencrypt/live/example.com/cert.pem;
        ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
        ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:AES:CAMELLIA:DES-CBC3-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!aECDH:!EDH-DSS-DES-CBC3-SHA:!EDH-RSA-DES-CBC3-SHA:!KRB5-DES-CBC3-SHA';
        ssl_prefer_server_ciphers on;
        
        gzip on;
        gzip_buffers 16 8k;
        gzip_comp_level 6;
        gzip_http_version 1.1;
        gzip_min_length 256;
        gzip_proxied any;
        gzip_vary on;
        gzip_types
            text/xml application/xml application/atom+xml application/rss+xml application/xhtml+xml image/svg+xml
            text/javascript application/javascript application/x-javascript
            text/x-json application/json application/x-web-app-manifest+json
            text/css text/plain text/x-component
            font/opentype application/x-font-ttf application/vnd.ms-fontobject
            image/x-icon;
        gzip_disable "msie6";
        
        auth_basic "My IoT";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        location / {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }
    }
}
```

## `.htpasswd`

Create credentials file for HTTP Basic Authentication for your username:

```bash
sudo apt-get install apache2-utils
htpasswd -c .htpasswd [username]
```

## `automation.py`

Here lives your configuration and automation. Start with the following `automation.py` file:

```python
# TODO
```

It's strictly advised to keep it under version control. [GitHub](https://github.com/) allows you to have a private repo for free.

## `docker-compose.yml`

We're almost ready to bring it up. Create the `docker-compose.yml`. Here you'll need to ensure that it contains correct paths to your:
- SQLite database file
- Nginx configuration file

The following configuration provides good defaults for Raspberry Pi:

```yaml
version: '3.7'
services:
  my-iot:
    container_name: my-iot
    image: eigenein/my-iot:latest
    restart: always
    network_mode: 'host'
    volumes:
    - './my-iot.sqlite3:/app/db.sqlite3'
    - './automation.py:/app/automation.py'
    environment:
      TZ: 'Europe/Amsterdam'
      MY_IOT_VERBOSITY: '2'
  nginx:
    container_name: nginx
    image: nginx
    restart: always
    network_mode: 'host'
    volumes:
    - './nginx.conf:/etc/nginx/nginx.conf:ro'
    - './.htpasswd:/etc/nginx/.htpasswd:ro'
    - '/etc/letsencrypt/:/etc/letsencrypt/:ro'
```

Pay attention, that `network_mode: 'host'` is needed for My IoT to talk to other devices.

And finally, just do:

```bash
docker-compose up -d
```
