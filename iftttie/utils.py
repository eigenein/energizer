from __future__ import annotations

from asyncio import Queue
from types import ModuleType
from typing import AsyncIterable, TypeVar

import click
from aiohttp import StreamReader
from click import echo, style
from passlib.handlers.pbkdf2 import pbkdf2_sha256

T = TypeVar('T')


async def read_lines(reader: StreamReader) -> AsyncIterable[str]:
    """
    Provides async iterable interface for a reader.
    """
    while True:
        line: bytes = await reader.readline()
        if not line:
            break
        yield line.decode()


async def iterate_queue(queue: Queue[T]) -> AsyncIterable[T]:
    """
    Provides async iterable interface for a queue.
    """
    while True:
        yield await queue.get()


def import_from_string(name: str, code: str) -> ModuleType:
    """
    Imports module from code passed as the parameter.
    """
    module = ModuleType(name)
    module.__package__ = 'iftttie'
    exec(code, module.__dict__)
    return module


@click.group()
def main():
    """
    IFTTTie utils.
    """
    pass


@main.command()
@click.password_option('-p', '--password')
def hash_password(password: str):
    """
    Print password hash for the IFTTTie dashboard authentication.
    """
    hash_ = pbkdf2_sha256.hash(password)

    echo()
    echo(style('Success! Put the following to your configuration module:', fg='green'))
    echo()
    echo(style(f"USERS = [\n    ('username', '{hash_}'),\n]", fg="yellow"))
    echo()


if __name__ == '__main__':
    main()
