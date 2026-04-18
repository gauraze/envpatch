import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_dedupe import dedupe_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_check_no_duplicates(runner, tmp_path):
    f = write(tmp_path, ".env", "A=1\nB=2\n")
    result = runner.invoke(dedupe_cmd, ["check", str(f)])
    assert result.exit_code == 0
    assert "No duplicate" in result.output


def test_check_finds_duplicate(runner, tmp_path):
    f = write(tmp_path, ".env", "A=1\nB=2\nA=3\n")
    result = runner.invoke(dedupe_cmd, ["check", str(f)])
    assert result.exit_code != 0
    assert "DUPLICATE" in result.output
    assert "A" in result.output


def test_fix_removes_duplicate_keep_last(runner, tmp_path):
    f = write(tmp_path, ".env", "A=first\nB=2\nA=last\n")
    result = runner.invoke(dedupe_cmd, ["fix", str(f), "--keep", "last"])
    assert result.exit_code == 0
    content = f.read_text()
    assert "A=last" in content
    assert "A=first" not in content


def test_fix_dry_run_does_not_write(runner, tmp_path):
    original = "A=1\nA=2\nB=3\n"
    f = write(tmp_path, ".env", original)
    result = runner.invoke(dedupe_cmd, ["fix", str(f), "--dry-run"])
    assert result.exit_code == 0
    assert f.read_text() == original


def test_fix_no_duplicates_unchanged(runner, tmp_path):
    f = write(tmp_path, ".env", "A=1\nB=2\n")
    result = runner.invoke(dedupe_cmd, ["fix", str(f)])
    assert result.exit_code == 0
    assert "unchanged" in result.output
