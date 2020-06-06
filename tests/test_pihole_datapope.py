#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""
import textwrap

import pytest
from click.testing import CliRunner

from pihole_datapope.capture import tcp_http_filter, as_bytestring

from pihole_datapope.utils import is_in_file, insert_in


def test_tcp_http_filter():
    r = tcp_http_filter(methods=('GET', 'POST'))
    assert r == "-s 0 -A 'tcp dst port 80 or " \
                "tcp dst port 443 and " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 or " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'"


# def test_temp():
#     cmd = stream_dump('eth0')
#     print(cmd)
#     assert False

# def test_command_parse():
#     """Test the CLI."""
#     runner = CliRunner()
#     result = runner.invoke(datapope_cli)
#     assert result.exit_code == 0
#     assert 'datapope is a log scrambler' in result.output
#     help_result = runner.invoke(datapope_cli, ['--help'])
#     assert help_result.exit_code == 0

content = textwrap.dedent("""
        Bogus
        config = 12

        # Comment
        [ Main ]

        config = 12
    """)


# def test_insert_in(temp_file):
#     fp = temp_file(content)
#     match = insert_in(fp, 'bogus', at_occurrence='Config')
#     assert match


def test_ensure_is_in_file(temp_file):

    ensure_txt = textwrap.dedent("""
        [ Main ]
        config = 12
    """)

    fp = temp_file(content)
    assert is_in_file(ensure_txt, fp)


@pytest.mark.parametrize('method,out', [
    ('GET ', '0x47455420'),
    ('GET', '0x474554'),
    ('POST', '0x504F5354'),
])
def test_as_bytestring(method, out):
    assert as_bytestring(method) == out
