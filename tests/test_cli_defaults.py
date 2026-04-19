"""Tests for envpatch.cli_defaults."""
from __future__ import annotations
import os
import pytest
from click.testing import CliRunner
from envpatch.cli_defaults import defaults_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_apply_adds_missing_key(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(defaults_cmd, ["apply", f, "--set", "BAZ=qux"])
    assert result.exit_code == 0
    assert "applied: BAZ" in result.output
    assert "BAZ=qux" in open(f).read()


def test_apply_skips_existing_key(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(defaults_cmd, ["apply", f, "--set", "FOO=new"])
    assert result.exit_code == 0
    assert "skipped" in result.output
    assert open(f).read().strip() == "FOO=bar"


def test_apply_overwrite_flag(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(defaults_cmd, ["apply", f, "--set", "FOO=new", "--overwrite"])
    assert result.exit_code == 0
    assert "FOO=new" in open(f).read()


def test_dry_run_does_not_write(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(defaults_cmd, ["apply", f, "--set", "BAZ=qux", "--dry-run"])
    assert result.exit_code == 0
    assert "BAZ=qux" in result.output
    assert "BAZ" not in open(f).read()


def test_missing_file_raises(runner, tmp_path):
    result = runner.invoke(defaults_cmd, ["apply", str(tmp_path / "missing.env"), "--set", "K=V"])
    assert result.exit_code != 0


def test_no_pairs_raises(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(defaults_cmd, ["apply", f])
    assert result.exit_code != 0
