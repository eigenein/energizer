from __future__ import annotations

import logging

import click


def setup_logging():
    logging.basicConfig(
        format='%(asctime)s [%(levelname).1s] (%(name)s) %(message)s',
        stream=click.get_text_stream('stderr'),
        datefmt='%b %d %H:%M:%S',
        level=logging.DEBUG,
    )
