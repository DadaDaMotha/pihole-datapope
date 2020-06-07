import click
from pihole_datapope.capture import stream_dump


@click.command()
def parse():
    """ Parse a logfile. """
    cmd = stream_dump('br0', incoming=(80, 443), outgoing=None)
    print(cmd)
