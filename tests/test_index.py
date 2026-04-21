"""Tests for envpatch.index."""
from __future__ import annotations

import pytest
from pathlib import Path

from envpatch.index import build_index, IndexEntry, IndexResult


@pytest.fixture
def env_dir(tmp_path: Path) -> Path:
    return tmp_path


def write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def test_build_index_single_file(env_dir):
    f = write(env_dir / ".env", "FOO=bar\nBAZ=qux\n")
    result = build_index([f])
    assert len(result.entries) == 2
    keys = {e.key for e in result.entries}
    assert keys == {"FOO", "BAZ"}


def test_build_index_multiple_files(env_dir):
    f1 = write(env_dir / "dev.env", "DB_HOST=localhost\nDB_PORT=5432\n")
    f2 = write(env_dir / "prod.env", "DB_HOST=prod.db\nAPI_KEY=secret\n")
    result = build_index([f1, f2])
    assert len(result.entries) == 4
    assert len(result.sources()) == 2


def test_find_key_returns_all_occurrences(env_dir):
    f1 = write(env_dir / "a.env", "HOST=localhost\n")
    f2 = write(env_dir / "b.env", "HOST=remotehost\n")
    result = build_index([f1, f2])
    hits = result.find_key("HOST")
    assert len(hits) == 2
    values = {h.value for h in hits}
    assert values == {"localhost", "remotehost"}


def test_find_in_source(env_dir):
    f1 = write(env_dir / "x.env", "A=1\nB=2\n")
    f2 = write(env_dir / "y.env", "C=3\n")
    result = build_index([f1, f2])
    entries = result.find_in_source(f1)
    assert len(entries) == 2
    assert all(e.source == f1 for e in entries)


def test_duplicates_detects_cross_file_keys(env_dir):
    f1 = write(env_dir / "base.env", "SHARED=one\nUNIQUE=only_here\n")
    f2 = write(env_dir / "override.env", "SHARED=two\n")
    result = build_index([f1, f2])
    dupes = result.duplicates()
    assert "SHARED" in dupes
    assert "UNIQUE" not in dupes
    assert len(dupes["SHARED"]) == 2


def test_keys_returns_sorted_unique(env_dir):
    f = write(env_dir / ".env", "ZEBRA=z\nAPPLE=a\nMIDDLE=m\n")
    result = build_index([f])
    assert result.keys() == ["APPLE", "MIDDLE", "ZEBRA"]


def test_missing_file_raises(env_dir):
    with pytest.raises(FileNotFoundError):
        build_index([str(env_dir / "nonexistent.env")])


def test_clean_true_when_no_entries(env_dir):
    f = write(env_dir / "empty.env", "")
    result = build_index([f])
    assert result.clean is True


def test_index_entry_str(env_dir):
    f = write(env_dir / "test.env", "KEY=val\n")
    result = build_index([f])
    entry = result.entries[0]
    assert "KEY=val" in str(entry)
    assert f in str(entry)
