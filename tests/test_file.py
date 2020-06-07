#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""
import textwrap

import pytest
from click.testing import CliRunner

from pihole_datapope.capture import tcp_http_filter, as_bytestring
from pihole_datapope.utils.file import insert_in, containing, START_BLOCK, \
    END_BLOCK


def test_tcp_http_filter():
    r = tcp_http_filter(methods=('GET', 'POST'))
    assert r == "-s 0 -A 'tcp dst port 80 or " \
                "tcp dst port 443 and " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 or " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'"


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


@pytest.mark.parametrize('where,prepend', [
    ('# Comment', False),
    ('config = 12', True),
])
def test_insert_in(where, prepend, temp_file):
    fp = temp_file(content)
    insert_in(fp, 'XXX', where, match_line=True, prepend=prepend, backup=False)
    with open(fp, 'r') as f:
        text = f.read()

    text_lines = text.split('\n')
    where_ix = text_lines.index(where)
    result_ix = text_lines.index('XXX')
    start_ix = text_lines.index(START_BLOCK)
    end_ix = text_lines.index(END_BLOCK)
    print(text)

    if prepend:
        assert end_ix == where_ix - 1
        assert result_ix == where_ix - 2
        assert start_ix == where_ix - 3
    else:
        assert start_ix == where_ix + 1
        assert result_ix == where_ix + 2
        assert end_ix == where_ix + 3


def insert_in_failing(temp_file):
    fp = temp_file('X')
    with pytest.raises(ValueError):
        insert_in(fp, '#', 'hello')


def test_is_in_file(temp_file):
    fp = temp_file(content)
    ensure_txt = textwrap.dedent("""
        [ Main ]

        config = 12
    """)
    assert containing(fp, ensure_txt)
    assert not containing(fp, "[ Main ]\nconfig = 12")


@pytest.mark.parametrize('method,out', [
    ('GET ', '0x47455420'),
    ('GET', '0x474554'),
    ('POST', '0x504F5354'),
])
def test_as_bytestring(method, out):
    assert as_bytestring(method) == out