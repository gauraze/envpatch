import pytest
from click.testing import CliRunner
from envpatch.cli_placeholder import placeholder_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_check_clean_env(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\nPORT=5432\n")
    result = runner.invoke(placeholder_cmd, ["check", f])
    assert result.exit_code == 0
    assert "No placeholder" in result.output


def test_check_detects_changeme(runner, tmp_path):
    f = write(tmp_path, ".env", "SECRET=CHANGEME\n")
    result = runner.invoke(placeholder_cmd, ["check", f])
    assert result.exit_code == 1
    assert "SECRET" in result.output


def test_check_quiet_flag_suppresses_success(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\n")
    result = runner.invoke(placeholder_cmd, ["check", f, "--quiet"])
    assert result.exit_code == 0
    assert result.output.strip() == ""


def test_check_missing_file(runner):
    result = runner.invoke(placeholder_cmd, ["check", "/nonexistent/.env"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "Error" in result.output


def test_check_custom_pattern(runner, tmp_path):
    f = write(tmp_path, ".env", "TOKEN=OVERRIDE_ME\n")
    result = runner.invoke(placeholder_cmd, ["check", f, "--pattern", "OVERRIDE_ME"])
    assert result.exit_code == 1
    assert "TOKEN" in result.output


def test_check_key_filter(runner, tmp_path):
    f = write(tmp_path, ".env", "A=CHANGEME\nB=CHANGEME\n")
    result = runner.invoke(placeholder_cmd, ["check", f, "--key", "A"])
    assert result.exit_code == 1
    assert "A" in result.output
    assert "B" not in result.output
