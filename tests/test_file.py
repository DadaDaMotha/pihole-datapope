#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""
import re
import textwrap

import pytest

from pihole_datapope.capture import tcp_http_filter, as_bytestring
from pihole_datapope.utils.file import insert_in, containing, START_BLOCK, \
    END_BLOCK, with_blocks, replace_key_value, replace_in, \
    MissingEditBlockException, read_file


def test_tcp_http_filter():
    r = tcp_http_filter(methods=('GET', 'POST'))
    assert r == "-s 0 -A 'tcp dst port 80 or " \
                "tcp dst port 443 and " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420 or " \
                "tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x504F5354'"


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
    text = read_file(fp)

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


@pytest.mark.parametrize('pattern,replace,output,blocks', [
    (r'custom', 'custOM', with_blocks('custOM\n# \nkey: val'), False),
    (r'(key: )([a-z]+)', r'\1PP', with_blocks('custom\n# \nkey: PP'), False),
    (r'bb', r'xx', with_blocks('custom\n# \nkey: val'), True),
])
def test_replace_in(pattern, replace, output, blocks, temp_file):
    fp = temp_file(with_blocks('custom\n# \nkey: val'))
    replace_in(fp, re.compile(pattern), replace, assert_blocks=blocks)
    assert read_file(fp) == output


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


def test_replace_in_no_outside(temp_file):
    original = textwrap.dedent(f"""
    interface eth0
    {START_BLOCK}
    interface wlan0
    {END_BLOCK}
    """)
    fp = temp_file(original)
    pattern = re.compile(r'^(interface )(.*?)$')
    replace_in(fp, pattern, replace=r'\1wlan1', assert_blocks=True)
    assert read_file(fp) == original.replace('wlan0', 'wlan1')


@pytest.mark.parametrize('block,assert_blocks', [
    (START_BLOCK, True),
    (END_BLOCK, True),
    (START_BLOCK, False),
    (END_BLOCK, False),
])
def test_replace_in_blocks(block, assert_blocks, temp_file):
    original = with_blocks('content')
    fp = temp_file(original)
    replace_in(fp, re.compile(block), 'X', assert_blocks=assert_blocks)
    assert read_file(fp) == original


def test_replace_in_ntimes(temp_file):
    original = textwrap.dedent(
        """
        alias BYE="/QUIT"
        alias BYE="/QUITT"
        alias BYE=
        """)
    fp = temp_file(original)
    replace_in(
        fp, re.compile(r'alias BYE=.*?$'), '', ntimes=2, assert_blocks=False)
    content = read_file(fp)
    assert content == "\n\n\nalias BYE=\n"


def test_replace_in_ltimes(temp_file):
    fp = temp_file('-up br -d br -t br')
    pattern = re.compile('br')
    replace_in(fp, pattern, 'X', ltimes=1, assert_blocks=False)
    assert read_file(fp) == "-up X -d br -t br"
    replace_in(fp, pattern, 'X', assert_blocks=False)
    assert read_file(fp) == "-up X -d X -t X"
