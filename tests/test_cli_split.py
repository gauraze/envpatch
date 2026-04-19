import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_split import split_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_split_writes_files(runner, tmp_path):
    src = write(tmp_path, ".env", "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=myapp\n")
    result = runner.invoke(split_cmd, ["run", src, "-p", "DB", "-p", "APP", "--outdir", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".env.db").exists()
    assert (tmp_path / ".env.app").exists()


def test_split_dry_run_no_write(runner, tmp_path):
    src = write(tmp_path, ".env", "DB_HOST=localhost\n")
    result = runner.invoke(split_cmd, ["run", src, "-p", "DB", "--outdir", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert not (tmp_path / ".env.db").exists()
    assert "DB_HOST=localhost" in result.output


def test_split_ungrouped_written(runner, tmp_path):
    src = write(tmp_path, ".env", "DB_HOST=localhost\nSECRET=abc\n")
    result = runner.invoke(split_cmd, ["run", src, "-p", "DB", "--outdir", str(tmp_path)])
    assert result.exit_code == 0
    assert (tmp_path / ".env.other").exists()
    assert "SECRET=abc" in (tmp_path / ".env.other").read_text()


def test_split_strip_prefix_flag(runner, tmp_path):
    src = write(tmp_path, ".env", "DB_HOST=localhost\n")
    result = runner.invoke(split_cmd, ["run", src, "-p", "DB", "--outdir", str(tmp_path), "--no-keep-prefix"])
    assert result.exit_code == 0
    content = (tmp_path / ".env.db").read_text()
    assert "HOST=localhost" in content
