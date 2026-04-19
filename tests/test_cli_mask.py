import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_mask import mask_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_mask_sensitive_stdout(runner, tmp_path):
    f = write(tmp_path, ".env", "API_SECRET=abc\nHOST=localhost\n")
    result = runner.invoke(mask_cmd, ["run", str(f)])
    assert result.exit_code == 0
    assert "API_SECRET=***" in result.output
    assert "HOST=localhost" in result.output


def test_mask_writes_to_output(runner, tmp_path):
    f = write(tmp_path, ".env", "DB_PASSWORD=hunter2\n")
    out = tmp_path / "masked.env"
    result = runner.invoke(mask_cmd, ["run", str(f), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "***" in out.read_text()


def test_mask_dry_run_does_not_write(runner, tmp_path):
    f = write(tmp_path, ".env", "TOKEN=xyz\n")
    out = tmp_path / "out.env"
    result = runner.invoke(mask_cmd, ["run", str(f), "--output", str(out), "--dry-run"])
    assert result.exit_code == 0
    assert not out.exists()


def test_mask_explicit_key(runner, tmp_path):
    f = write(tmp_path, ".env", "CUSTOM=value\nSAFE=ok\n")
    result = runner.invoke(mask_cmd, ["run", str(f), "--key", "CUSTOM"])
    assert "CUSTOM=***" in result.output
    assert "SAFE=ok" in result.output


def test_mask_no_matches_reports(runner, tmp_path):
    f = write(tmp_path, ".env", "HOST=localhost\n")
    result = runner.invoke(mask_cmd, ["run", str(f)])
    assert result.exit_code == 0
    assert "No keys matched" in result.output
