#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""

import pytest

from click.testing import CliRunner

from pihole_datapope.loader import datapope_cli


def test_command_parse():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(datapope_cli)
    assert result.exit_code == 0
    assert 'datapope is a log scrambler' in result.output
    help_result = runner.invoke(datapope_cli, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output
