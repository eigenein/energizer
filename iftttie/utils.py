from __future__ import annotations

import click
from click import echo, style
from passlib.handlers.pbkdf2 import pbkdf2_sha256


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
