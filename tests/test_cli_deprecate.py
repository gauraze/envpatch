import pytest
from click.testing import CliRunner
from envpatch.cli_deprecate import deprecate_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_check_no_deprecated(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\nPORT=8080\n")
    result = runner.invoke(deprecate_cmd, ["check", f, "--key", "OLD:gone"])
    assert result.exit_code == 0
    assert "No deprecated" in result.output


def test_check_finds_deprecated(runner, tmp_path):
    f = write(tmp_path, ".env", "OLD_HOST=localhost\n")
    result = runner.invoke(deprecate_cmd, ["check", f, "--key", "OLD_HOST:use HOST instead:HOST"])
    assert result.exit_code == 1
    assert "DEPRECATED" in result.output
    assert "OLD_HOST" in result.output


def test_apply_renames_key(runner, tmp_path):
    f = write(tmp_path, ".env", "OLD_HOST=localhost\n")
    result = runner.invoke(deprecate_cmd, ["apply", f, "--key", "OLD_HOST:renamed:HOST"])
    assert result.exit_code == 0
    assert "renamed" in result.output
    content = open(f).read()
    assert "HOST=" in content
    assert "OLD_HOST" not in content


def test_apply_dry_run_does_not_write(runner, tmp_path):
    f = write(tmp_path, ".env", "OLD=val\n")
    original = open(f).read()
    result = runner.invoke(deprecate_cmd, ["apply", f, "--key", "OLD:gone:NEW", "--dry-run"])
    assert result.exit_code == 0
    assert open(f).read() == original


def test_apply_drops_key(runner, tmp_path):
    f = write(tmp_path, ".env", "LEGACY=old\nKEEP=yes\n")
    result = runner.invoke(deprecate_cmd, ["apply", f, "--key", "LEGACY:removed:DROP"])
    assert result.exit_code == 0
    content = open(f).read()
    assert "LEGACY" not in content
    assert "KEEP" in content
