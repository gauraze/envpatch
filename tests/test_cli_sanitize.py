import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_sanitize import sanitize_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_sanitize_clean_env(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\nPORT=5432\n")
    result = runner.invoke(sanitize_cmd, ["run", f])
    assert result.exit_code == 0
    assert "No issues found" in result.output


def test_sanitize_strips_whitespace(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=  localhost  \n")
    result = runner.invoke(sanitize_cmd, ["run", f])
    assert result.exit_code == 0
    assert "issue" in result.output


def test_sanitize_dry_run_does_not_write(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=  localhost  \n")
    out = str(tmp_path / "out.env")
    result = runner.invoke(sanitize_cmd, ["run", f, "--output", out, "--dry-run"])
    assert result.exit_code == 0
    assert not Path(out).exists()


def test_sanitize_writes_output_file(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=  localhost  \n")
    out = str(tmp_path / "out.env")
    result = runner.invoke(sanitize_cmd, ["run", f, "--output", out])
    assert result.exit_code == 0
    assert Path(out).exists()
    assert "HOST=localhost" in Path(out).read_text()


def test_sanitize_remove_empty(runner, tmp_path):
    f = write(tmp_path, ".env", "EMPTY=\nFULL=yes\n")
    out = str(tmp_path / "out.env")
    result = runner.invoke(sanitize_cmd, ["run", f, "--remove-empty", "--output", out])
    assert result.exit_code == 0
    content = Path(out).read_text()
    assert "EMPTY" not in content
    assert "FULL=yes" in content
