import click

from pihole_datapope.cli import info, plain, warn
from pihole_datapope.config import read_config


@click.command()
def parse():
    """ Parse a logfile. """
    config = read_config()
    for k, v in config.items():
        info(f"{k} - {v}")
