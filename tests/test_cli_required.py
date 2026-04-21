import pytest
from click.testing import CliRunner
from envpatch.cli_required import required_cmd
import os


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_check_passes_all_present(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\nBAZ=qux\n")
    result = runner.invoke(required_cmd, ["check", f, "-k", "FOO", "-k", "BAZ"])
    assert result.exit_code == 0
    assert "All required keys present" in result.output


def test_check_fails_on_missing_key(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(required_cmd, ["check", f, "-k", "FOO", "-k", "MISSING"])
    assert result.exit_code != 0
    assert "MISSING" in result.output


def test_check_fails_on_empty_value(runner, tmp_path):
    f = write(tmp_path, ".env", "SECRET=\n")
    result = runner.invoke(required_cmd, ["check", f, "-k", "SECRET"])
    assert result.exit_code != 0
    assert "SECRET" in result.output


def test_check_passes_empty_with_allow_empty(runner, tmp_path):
    f = write(tmp_path, ".env", "SECRET=\n")
    result = runner.invoke(required_cmd, ["check", f, "-k", "SECRET", "--allow-empty"])
    assert result.exit_code == 0
    assert "All required keys present" in result.output


def test_check_fails_on_nonexistent_file(runner, tmp_path):
    missing_file = str(tmp_path / "nonexistent.env")
    result = runner.invoke(required_cmd, ["check", missing_file, "-k", "FOO"])
    assert result.exit_code != 0
