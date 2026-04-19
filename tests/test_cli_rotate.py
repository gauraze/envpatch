import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_rotate import rotate_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_rotate_writes_new_value(runner, tmp_path):
    f = write(tmp_path, ".env", "SECRET=old\nFOO=bar\n")
    result = runner.invoke(rotate_cmd, ["run", f, "--set", "SECRET=newval"])
    assert result.exit_code == 0
    assert "rotated: SECRET" in result.output
    assert "SECRET=newval" in Path(f).read_text()


def test_rotate_dry_run_does_not_write(runner, tmp_path):
    f = write(tmp_path, ".env", "SECRET=old\n")
    result = runner.invoke(rotate_cmd, ["run", f, "--set", "SECRET=new", "--dry-run"])
    assert result.exit_code == 0
    assert "SECRET=old" in Path(f).read_text()


def test_rotate_missing_key_shows_skipped(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(rotate_cmd, ["run", f, "--set", "MISSING=x"])
    assert result.exit_code == 0
    assert "Nothing rotated" in result.output


def test_rotate_invalid_pair_exits(runner, tmp_path):
    f = write(tmp_path, ".env", "FOO=bar\n")
    result = runner.invoke(rotate_cmd, ["run", f, "--set", "NOEQUALSSIGN"])
    assert result.exit_code != 0


def test_rotate_output_to_separate_file(runner, tmp_path):
    src = write(tmp_path, ".env", "TOKEN=abc\n")
    out = str(tmp_path / ".env.rotated")
    result = runner.invoke(rotate_cmd, ["run", src, "--set", "TOKEN=xyz", "--output", out])
    assert result.exit_code == 0
    assert "TOKEN=xyz" in Path(out).read_text()
    assert "TOKEN=abc" in Path(src).read_text()
