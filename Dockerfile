FROM python:3.7
FROM resin/raspberry-pi-python:3.7-stretch
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8 PYTHONOPTIMIZE=1

# https://stackoverflow.com/questions/1189389/python-non-privileged-icmp
RUN apt-get update && apt-get install -y libcap2-bin && rm -rf /var/lib/apt/lists/*
RUN setcap cap_net_raw=ep /usr/local/bin/python3.7

RUN pip install --no-cache-dir --upgrade ipython pip

COPY requirements.txt /tmp/iftttie/requirements.txt
RUN pip install --no-cache-dir -r /tmp/iftttie/requirements.txt
COPY . /tmp/iftttie
RUN pip install --no-cache-dir --no-deps /tmp/iftttie && rm -r /tmp/iftttie

RUN mkdir /app && touch /app/db.sqlite3 && chown -R nobody:nogroup /app
WORKDIR /app

USER nobody:nogroup
EXPOSE 8443
STOPSIGNAL SIGINT
ENTRYPOINT ["iftttie"]
CMD []
