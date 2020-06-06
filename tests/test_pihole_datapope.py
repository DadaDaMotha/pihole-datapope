#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""
import textwrap

import pytest

from click.testing import CliRunner

from pihole_datapope.capture import stream_dump, tcp_http_filter
from pihole_datapope.config import read_config
from pihole_datapope.loader import datapope_cli


def test_tcp_http_filter():
    r = tcp_http_filter(methods=('GET', 'POST'))
    assert r == "-s 0 -A 'tcp dst port 80 and " \
                "tcp dst port 443 and " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 and " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'"


def test_temp():
    cmd = stream_dump('eth0')
    print(cmd)
    assert False

# def test_command_parse():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(datapope_cli)
#     assert result.exit_code == 0
#     assert 'datapope is a log scrambler' in result.output
#     help_result = runner.invoke(datapope_cli, ['--help'])
#     assert help_result.exit_code == 0
#     assert '--help' in help_result.output

def test_ensure_in_file():
    sample_file = textwrap.dedent("""
        Bogus

        config = 12
    """)
