import click

from pihole_datapope.cli import info, plain, warn


@click.command()
def parse():
    """ Parse a logfile. """

    
