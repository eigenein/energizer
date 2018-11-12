from __future__ import annotations

import logging
from typing import Optional, Tuple

import click

from iftttie import utils, web

logger = logging.getLogger('iftttie')


@click.command()
@click.option('--http-port', type=int, default=8080, help='HTTP port.')
@click.option('access_tokens', '--access-token', type=str, required=True, multiple=True, help='IFTTTie access token.')
@click.option('--ifttt-token', type=str, default=None, help='IFTTT Webhooks token.')
@click.option('--nest-token', type=str, default=None, help='NEST API OAuth token.')
@click.option('--buienradar-station-id', type=int, default=None, help='Buienradar.nl station ID.')
def main(
    http_port: int,
    access_tokens: Tuple[str, ...],
    ifttt_token: Optional[str],
    nest_token: Optional[str],
    buienradar_station_id: Optional[int],
):
    utils.setup_logging()
    logger.info('🚀 IFFTTie is starting…')
    web.run(http_port, set(access_tokens))
    logger.info('🛬 IFFTTie stopped.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
