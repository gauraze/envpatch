"""Tests for envpatch.cli_resolve."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envpatch.cli_resolve import resolve_cmd


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_resolve_fills_empty_from_fallback(runner, tmp_path):
    base = write(tmp_path, ".env", "FOO=\nBAR=kept\n")
    fb = write(tmp_path, ".env.fb", "FOO=filled\nBAR=ignored\n")
    result = runner.invoke(resolve_cmd, ["run", str(base), str(fb)])
    assert result.exit_code == 0
    assert "FOO" in base.read_text()
    assert "filled" in base.read_text()


def test_resolve_dry_run_does_not_write(runner, tmp_path):
    base = write(tmp_path, ".env", "FOO=\n")
    fb = write(tmp_path, ".env.fb", "FOO=fromfb\n")
    original = base.read_text()
    result = runner.invoke(resolve_cmd, ["run", str(base), str(fb), "--dry-run"])
    assert result.exit_code == 0
    assert base.read_text() == original
    assert "fromfb" in result.output


def test_resolve_writes_to_output_file(runner, tmp_path):
    base = write(tmp_path, ".env", "FOO=\n")
    fb = write(tmp_path, ".env.fb", "FOO=resolved\n")
    out = tmp_path / "out.env"
    result = runner.invoke(resolve_cmd, ["run", str(base), str(fb), "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()
    assert "FOO=resolved" in out.read_text()


def test_resolve_exits_nonzero_when_unresolved(runner, tmp_path):
    base = write(tmp_path, ".env", "FOO=\nBAR=\n")
    fb = write(tmp_path, ".env.fb", "FOO=filled\n")
    result = runner.invoke(resolve_cmd, ["run", str(base), str(fb)])
    assert result.exit_code == 1


def test_resolve_overwrite_flag(runner, tmp_path):
    base = write(tmp_path, ".env", "FOO=original\n")
    fb = write(tmp_path, ".env.fb", "FOO=replacement\n")
    result = runner.invoke(resolve_cmd, ["run", str(base), str(fb), "--overwrite"])
    assert result.exit_code == 0
    assert "replacement" in base.read_text()
