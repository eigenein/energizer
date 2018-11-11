import logging
from typing import Optional

import click

from iftttie import utils, web


@click.command()
@click.option('--http-port', type=int, default=8000, help='HTTP port.')
@click.option('--ifttt-token', type=str, default=None, help='IFTTT Webhooks token.')
@click.option('--nest-token', type=str, default=None, help='NEST API OAuth token.')
@click.option('--buienradar-station-id', type=int, default=None, help='Buienradar.nl station ID.')
def main(
    http_port: int,
    ifttt_token: Optional[str],
    nest_token: Optional[str],
    buienradar_station_id: Optional[int],
):
    utils.setup_logging()
    logging.info('🚀 IFFTTie is starting…')
    web.run(http_port)
    logging.info('🛬 IFFTTie stopped.')


if __name__ == '__main__':
    main(auto_envvar_prefix='IFTTTIE')
