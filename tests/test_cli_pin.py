import pytest
from click.testing import CliRunner
from envpatch.cli_pin import pin_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_pin_check_passes(runner, tmp_path):
    f = write(tmp_path, ".env", "APP_ENV=production\nDEBUG=false\n")
    result = runner.invoke(pin_cmd, ["check", f, "--pin", "APP_ENV=production"])
    assert result.exit_code == 0
    assert "match" in result.output


def test_pin_check_fails_on_mismatch(runner, tmp_path):
    f = write(tmp_path, ".env", "APP_ENV=staging\n")
    result = runner.invoke(pin_cmd, ["check", f, "--pin", "APP_ENV=production"])
    assert result.exit_code == 1
    assert "APP_ENV" in result.output


def test_pin_check_no_pins(runner, tmp_path):
    f = write(tmp_path, ".env", "APP_ENV=staging\n")
    result = runner.invoke(pin_cmd, ["check", f])
    assert result.exit_code == 0
    assert "No pins" in result.output


def test_pin_apply_writes_file(runner, tmp_path):
    f = write(tmp_path, ".env", "APP_ENV=staging\nPORT=8080\n")
    result = runner.invoke(pin_cmd, ["apply", f, "--pin", "APP_ENV=production"])
    assert result.exit_code == 0
    assert "Applied" in result.output
    content = open(f).read()
    assert "APP_ENV=production" in content
    assert "PORT=8080" in content


def test_pin_apply_dry_run_does_not_write(runner, tmp_path):
    f = write(tmp_path, ".env", "APP_ENV=staging\n")
    result = runner.invoke(pin_cmd, ["apply", f, "--pin", "APP_ENV=production", "--dry-run"])
    assert result.exit_code == 0
    assert "APP_ENV=production" in result.output
    assert open(f).read() == "APP_ENV=staging\n"
