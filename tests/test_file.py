#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""
import re
import textwrap

import pytest
from click.testing import CliRunner

from pihole_datapope.capture import tcp_http_filter, as_bytestring
from pihole_datapope.utils.file import insert_in, containing, START_BLOCK, \
    END_BLOCK, with_blocks, replace_key_value, replace_in, \
    MissingEditBlockException


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


@pytest.mark.parametrize('input,key,output', [
    ('k_c = BB', 'k_c', 'k_c = XX'),
    ('k_c=BB', 'k_c', 'k_c=XX'),
    ('k_c=BB', 'k_', 'k_c=BB'),
    ('\nk_c=BB', 'k_c', '\nk_c=BB'),
    ('B=BB', 'B', 'B=XX'),
    ('B=BB', 'B', 'B=XX'),
    ('X=.?=*_$!^\\', 'X', 'X=XX')
])
def test_replace_key_value_pair(input, key, output):
    assert replace_key_value(input, key, 'XX') == output


@pytest.mark.parametrize('pattern,replace,output', [
    (r'custom', 'custOM', with_blocks('custOM\n# \nkey: val')),
    (r'(key: )([a-z]+)', r'\1PP', with_blocks('custom\n# \nkey: PP')),
])
def test_replace_in(pattern, replace, output, temp_file):
    fp = temp_file(with_blocks('custom\n# \nkey: val'))
    replace_in(fp, re.compile(pattern), replace, assert_blocks=False)
    with open(fp, 'r') as f:
        s = f.read()
    assert s == output


def test_replace_in_exceptions(temp_file):
    fp = temp_file('»')
    patt = re.compile('x')
    with pytest.raises(ValueError):
        replace_in(fp, 'x', 'y', assert_blocks=True)

    with pytest.raises(MissingEditBlockException):
        replace_in(fp, patt, 'y', assert_blocks=True)

    fp = temp_file(START_BLOCK + "\ncorrupted")
    with pytest.raises(MissingEditBlockException):
        replace_in(fp, patt, 'y', assert_blocks=True)
