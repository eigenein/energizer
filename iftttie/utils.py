from __future__ import annotations

from asyncio import Queue
from types import ModuleType
from typing import AsyncIterable, TypeVar

import click
from aiohttp import StreamReader
from argon2 import PasswordHasher
from click import echo, style

T = TypeVar('T')


async def read_lines(reader: StreamReader) -> AsyncIterable[str]:
    """Provides async iterable interface for a reader."""
    while True:
        line: bytes = await reader.readline()
        if not line:
            break
        yield line.decode()


async def iterate_queue(queue: Queue[T]) -> AsyncIterable[T]:
    """Provides async iterable interface for a queue."""
    while True:
        yield await queue.get()


def import_from_string(name: str, code: str) -> ModuleType:
    """Imports module from code passed as the parameter."""
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
    hash_ = hasher.hash(password)

    echo()
    echo(style("Success! Use this option to run `iftttie`:", fg="green"))
    echo(style(f"-u <login> '{hash_}'", fg="yellow"))
    echo()
    echo(f'Example {style("docker-compose.yml", fg="blue")} entry:')
    echo()
    echo(style('    environment:', fg='yellow'))
    echo(style(f"      IFTTTIE_USERS: '<login> {hash_.replace('$', '$$')}'", fg='yellow'))
    echo()


# Parameters adjusted for Raspberry Pi Zero W.
hasher = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)


if __name__ == '__main__':
    main()
