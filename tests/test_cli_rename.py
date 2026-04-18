import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_rename import rename_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> str:
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_rename_basic(runner, tmp_path):
    env = write(tmp_path, ".env", "OLD_KEY=hello\n")
    result = runner.invoke(rename_cmd, ["run", env, "-m", "OLD_KEY=NEW_KEY"])
    assert result.exit_code == 0
    assert "renamed: OLD_KEY -> NEW_KEY" in result.output
    assert "NEW_KEY=hello" in Path(env).read_text()


def test_rename_dry_run_does_not_write(runner, tmp_path):
    env = write(tmp_path, ".env", "OLD=abc\n")
    original = Path(env).read_text()
    result = runner.invoke(rename_cmd, ["run", env, "-m", "OLD=NEW", "--dry-run"])
    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert Path(env).read_text() == original


def test_rename_conflict_skipped(runner, tmp_path):
    env = write(tmp_path, ".env", "OLD=1\nNEW=2\n")
    result = runner.invoke(rename_cmd, ["run", env, "-m", "OLD=NEW"])
    assert "skipped" in result.output


def test_rename_to_separate_out_file(runner, tmp_path):
    env = write(tmp_path, ".env", "FOO=bar\n")
    out = str(tmp_path / "out.env")
    result = runner.invoke(rename_cmd, ["run", env, "-m", "FOO=BAZ", "--out", out])
    assert result.exit_code == 0
    assert "BAZ=bar" in Path(out).read_text()


def test_invalid_mapping_format(runner, tmp_path):
    env = write(tmp_path, ".env", "A=1\n")
    result = runner.invoke(rename_cmd, ["run", env, "-m", "BADFORMAT"])
    assert result.exit_code != 0
