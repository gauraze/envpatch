import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_tag import tag_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_tag_apply_basic(runner, tmp_path):
    env_file = write(tmp_path, ".env", "API_KEY=secret\nDEBUG=true\n")
    result = runner.invoke(tag_cmd, ["apply", env_file, "--tag", "API_KEY=sensitive"])
    assert result.exit_code == 0
    assert "Tagged 1" in result.output
    content = Path(env_file).read_text()
    assert "# [sensitive]" in content


def test_tag_apply_dry_run_does_not_write(runner, tmp_path):
    env_file = write(tmp_path, ".env", "API_KEY=secret\n")
    original = Path(env_file).read_text()
    result = runner.invoke(tag_cmd, ["apply", env_file, "--tag", "API_KEY=sensitive", "--dry-run"])
    assert result.exit_code == 0
    assert Path(env_file).read_text() == original
    assert "# [sensitive]" in result.output


def test_tag_apply_skipped_key_shown(runner, tmp_path):
    env_file = write(tmp_path, ".env", "API_KEY=secret\n")
    result = runner.invoke(tag_cmd, ["apply", env_file, "--tag", "MISSING=label"])
    assert result.exit_code == 0
    assert "MISSING" in result.output


def test_tag_apply_invalid_format(runner, tmp_path):
    env_file = write(tmp_path, ".env", "API_KEY=secret\n")
    result = runner.invoke(tag_cmd, ["apply", env_file, "--tag", "BADFORMAT"])
    assert result.exit_code != 0


def test_tag_apply_output_file(runner, tmp_path):
    env_file = write(tmp_path, ".env", "TOKEN=abc\n")
    out_file = str(tmp_path / "out.env")
    result = runner.invoke(tag_cmd, ["apply", env_file, "--tag", "TOKEN=auth", "--output", out_file])
    assert result.exit_code == 0
    assert "# [auth]" in Path(out_file).read_text()
