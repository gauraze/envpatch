"""Tests for envpatch.cli_stub."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_stub import stub_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_stub_generate_dry_run(runner, tmp_path):
    result = runner.invoke(stub_cmd, ["generate", "API_KEY", "DB_HOST", "--dry-run"])
    assert result.exit_code == 0
    assert "API_KEY=" in result.output
    assert "DB_HOST=" in result.output


def test_stub_generate_writes_file(runner, tmp_path):
    out = tmp_path / "out.env"
    result = runner.invoke(stub_cmd, ["generate", "FOO", "BAR", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    content = out.read_text()
    assert "FOO=" in content
    assert "BAR=" in content


def test_stub_generate_with_placeholder(runner, tmp_path):
    out = tmp_path / "out.env"
    result = runner.invoke(
        stub_cmd, ["generate", "SECRET", "--placeholder", "CHANGEME", "--output", str(out)]
    )
    assert result.exit_code == 0
    assert "SECRET=CHANGEME" in out.read_text()


def test_stub_generate_with_base_skips_existing(runner, tmp_path):
    base = write(tmp_path, ".env", "EXISTING=hello\n")
    result = runner.invoke(
        stub_cmd, ["generate", "EXISTING", "NEW_KEY", "--base", str(base), "--dry-run"]
    )
    assert result.exit_code == 0
    assert "EXISTING=hello" in result.output
    assert "NEW_KEY=" in result.output


def test_stub_generate_missing_base_errors(runner, tmp_path):
    result = runner.invoke(stub_cmd, ["generate", "KEY", "--base", "/no/such/file.env"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "not found" in (result.exception and str(result.exception) or "")
