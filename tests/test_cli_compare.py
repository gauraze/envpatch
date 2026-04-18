"""Tests for envpatch.cli_compare CLI commands."""
import os
import pytest
from click.testing import CliRunner
from envpatch.cli_compare import compare_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_compare_identical(runner, tmp_path):
    f = write(tmp_path, "a.env", "FOO=bar\n")
    result = runner.invoke(compare_cmd, ["run", f, f])
    assert result.exit_code == 0
    assert "identical" in result.output


def test_compare_shows_added(runner, tmp_path):
    base = write(tmp_path, "base.env", "FOO=bar\n")
    other = write(tmp_path, "other.env", "FOO=bar\nNEW=val\n")
    result = runner.invoke(compare_cmd, ["run", base, other])
    assert result.exit_code == 0
    assert "+ NEW" in result.output


def test_compare_shows_removed(runner, tmp_path):
    base = write(tmp_path, "base.env", "FOO=bar\nOLD=gone\n")
    other = write(tmp_path, "other.env", "FOO=bar\n")
    result = runner.invoke(compare_cmd, ["run", base, other])
    assert result.exit_code == 0
    assert "- OLD" in result.output


def test_compare_summary_flag(runner, tmp_path):
    base = write(tmp_path, "base.env", "A=1\nB=2\n")
    other = write(tmp_path, "other.env", "A=changed\nC=3\n")
    result = runner.invoke(compare_cmd, ["run", base, other, "--summary"])
    assert result.exit_code == 0
    assert "Added:" in result.output
    assert "Removed:" in result.output


def test_compare_modified_shows_arrow(runner, tmp_path):
    base = write(tmp_path, "base.env", "KEY=old\n")
    other = write(tmp_path, "other.env", "KEY=new\n")
    result = runner.invoke(compare_cmd, ["run", base, other])
    assert "->" in result.output
