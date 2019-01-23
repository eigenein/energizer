FROM python:3.7
FROM resin/raspberry-pi-python:3.7-stretch
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8 PYTHONOPTIMIZE=1

RUN apt-get update && apt-get install -y libcap2-bin && rm -rf /var/lib/apt/lists/*

# https://stackoverflow.com/questions/36215201/python-scapy-sniff-without-root
RUN setcap cap_net_raw=eip /usr/local/bin/python3.7

# This is quite useful for debugging in place.
RUN pip install --no-cache-dir ipython

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
