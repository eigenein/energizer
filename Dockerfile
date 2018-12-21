FROM python:3.7
FROM resin/raspberry-pi-python:3.7-stretch
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8

COPY requirements.txt /tmp/iftttie/requirements.txt
RUN pip install --no-cache-dir -r /tmp/iftttie/requirements.txt
COPY . /tmp/iftttie
RUN pip install --no-cache-dir --no-deps /tmp/iftttie && rm -r /tmp/iftttie

RUN mkdir /app && touch /app/db.sqlite3 && chown -R nobody:nogroup /app
WORKDIR /app

USER nobody:nogroup
STOPSIGNAL SIGINT
ENTRYPOINT ["iftttie"]
CMD []
