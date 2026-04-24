"""Integration tests for resolve: parse -> resolve -> serialize -> reparse."""
from __future__ import annotations

from pathlib import Path

import pytest

from envpatch.parser import EnvFile
from envpatch.resolve import resolve_env


@pytest.fixture()
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def _write(directory: Path, name: str, content: str) -> Path:
    p = directory / name
    p.write_text(content)
    return p


def test_roundtrip_resolve_and_reparse(env_dir):
    base_path = _write(env_dir, ".env", "FOO=\nBAR=hello\n")
    fb_path = _write(env_dir, ".env.fb", "FOO=world\n")

    base = EnvFile.parse(base_path.read_text())
    fb = EnvFile.parse(fb_path.read_text())
    result = resolve_env(base, [fb])

    out = result.to_dotenv()
    base_path.write_text(out)

    reparsed = EnvFile.parse(base_path.read_text())
    values = {e.key: e.value for e in reparsed.entries}
    assert values["FOO"] == "world"
    assert values["BAR"] == "hello"


def test_resolve_does_not_lose_keys(env_dir):
    base_path = _write(env_dir, ".env", "A=1\nB=\nC=3\n")
    fb_path = _write(env_dir, ".env.fb", "B=2\n")

    base = EnvFile.parse(base_path.read_text())
    fb = EnvFile.parse(fb_path.read_text())
    result = resolve_env(base, [fb])

    keys = [e.key for e in result.entries]
    assert "A" in keys
    assert "B" in keys
    assert "C" in keys


def test_resolve_multiple_fallbacks_priority(env_dir):
    base_path = _write(env_dir, ".env", "X=\n")
    fb1_path = _write(env_dir, ".env.1", "X=\n")
    fb2_path = _write(env_dir, ".env.2", "X=from_second\n")

    base = EnvFile.parse(base_path.read_text())
    fb1 = EnvFile.parse(fb1_path.read_text())
    fb2 = EnvFile.parse(fb2_path.read_text())
    result = resolve_env(base, [fb1, fb2])

    values = {e.key: e.value for e in result.entries}
    assert values["X"] == "from_second"
