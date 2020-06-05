#!/usr/bin/env python

"""Tests for `pihole_datapope` package."""

import pytest

from click.testing import CliRunner


def test_command_parse():
    """Test the CLI."""
    runner = CliRunner()
    # result = runner.invoke(parse)
    # assert result.exit_code == 0
    # assert 'pihole_datapope.cli.main' in result.output
    # help_result = runner.invoke(parse, ['--help'])
    # assert help_result.exit_code == 0
    # assert '--help' in help_result.output
