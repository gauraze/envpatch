import pytest
from click.testing import CliRunner
from envpatch.cli_normalize import normalize_cmd
import os


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_normalize_uppercases_keys(runner, tmp_path):
    f = write(tmp_path, ".env", "db_host=localhost\n")
    result = runner.invoke(normalize_cmd, ["run", f])
    assert result.exit_code == 0
    assert "key uppercased" in result.output
    assert "DB_HOST=localhost" in open(f).read()


def test_normalize_dry_run_does_not_write(runner, tmp_path):
    original = "db_host=localhost\n"
    f = write(tmp_path, ".env", original)
    result = runner.invoke(normalize_cmd, ["run", "--dry-run", f])
    assert result.exit_code == 0
    assert open(f).read() == original


def test_normalize_no_issues_message(runner, tmp_path):
    f = write(tmp_path, ".env", "DB_HOST=localhost\n")
    result = runner.invoke(normalize_cmd, ["run", f])
    assert "No normalization needed" in result.output


def test_normalize_output_flag_writes_new_file(runner, tmp_path):
    src = write(tmp_path, "src.env", "db_host=localhost\n")
    dest = str(tmp_path / "out.env")
    result = runner.invoke(normalize_cmd, ["run", src, "--output", dest])
    assert result.exit_code == 0
    assert os.path.exists(dest)
    assert "DB_HOST" in open(dest).read()


def test_normalize_strip_quotes(runner, tmp_path):
    f = write(tmp_path, ".env", 'API_KEY="secret"\n')
    result = runner.invoke(normalize_cmd, ["run", f, "--no-uppercase"])
    assert result.exit_code == 0
    assert 'API_KEY=secret' in open(f).read()
