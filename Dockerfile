FROM python:3.7
MAINTAINER Pavel Perestoronin <eigenein@gmail.com>

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 PYTHONIOENCODING=utf-8

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir --no-deps .

STOPSIGNAL SIGINT
ENTRYPOINT ["iftttie"]
CMD []
