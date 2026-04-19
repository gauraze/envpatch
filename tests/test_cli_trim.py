import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_trim import trim_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_trim_removes_key(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=1\nBAR=2\nBAZ=3")
    result = runner.invoke(trim_cmd, ["run", f, "--key", "BAR"])
    assert result.exit_code == 0
    assert "BAR" not in Path(f).read_text()
    assert "FOO=1" in Path(f).read_text()


def test_trim_dry_run_does_not_write(runner, tmp_path):
    original = "FOO=1\nBAR=2"
    f = write(tmp_path, ".env", original)
    result = runner.invoke(trim_cmd, ["run", f, "--key", "BAR", "--dry-run"])
    assert result.exit_code == 0
    assert Path(f).read_text() == original


def test_trim_by_prefix(runner, tmp_path):
    f = write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP=x")
    result = runner.invoke(trim_cmd, ["run", f, "--prefix", "DB_"])
    assert result.exit_code == 0
    content = Path(f).read_text()
    assert "DB_HOST" not in content
    assert "APP=x" in content


def test_trim_no_keys_removes_nothing(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=1\nBAR=2")
    result = runner.invoke(trim_cmd, ["run", f])
    assert result.exit_code == 0
    assert "No keys removed" in result.output


def test_trim_output_flag_writes_new_file(runner, tmp_path):
    src = write(tmp_path, ".env", "FOO=1\nBAR=2")
    out = str(tmp_path / "out.env")
    runner.invoke(trim_cmd, ["run", src, "--key", "FOO", "--output", out])
    assert Path(out).exists()
    assert "FOO" not in Path(out).read_text()
    assert "BAR=2" in Path(out).read_text()
