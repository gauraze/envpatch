"""Tests for envpatch.dedup_keys — cross-file duplicate key detection."""
import pytest

from envpatch.parser import EnvFile, EnvEntry
from envpatch.dedup_keys import (
    find_cross_duplicates,
    dedup_cross,
    CrossFileDupe,
    CrossDupeResult,
)


def make_env(pairs: dict) -> EnvFile:
    ef = EnvFile()
    for k, v in pairs.items():
        ef._entries.append(EnvEntry(key=k, value=v, raw=f"{k}={v}"))
    return ef


def test_no_duplicates_returns_clean():
    a = make_env({"FOO": "1", "BAR": "2"})
    b = make_env({"BAZ": "3"})
    result = dedup_cross([("a", a), ("b", b)])
    assert result.clean is True
    assert result.duplicates == []


def test_find_cross_duplicates_detects_shared_key():
    a = make_env({"FOO": "from_a"})
    b = make_env({"FOO": "from_b"})
    dupes = find_cross_duplicates([("a", a), ("b", b)])
    assert len(dupes) == 1
    assert dupes[0].key == "FOO"
    assert ("a", "from_a") in dupes[0].occurrences
    assert ("b", "from_b") in dupes[0].occurrences


def test_dedup_cross_keep_last_wins():
    a = make_env({"FOO": "first"})
    b = make_env({"FOO": "second"})
    result = dedup_cross([("a", a), ("b", b)], keep="last")
    assert result.merged.get("FOO") == "second"


def test_dedup_cross_keep_first_wins():
    a = make_env({"FOO": "first"})
    b = make_env({"FOO": "second"})
    result = dedup_cross([("a", a), ("b", b)], keep="first")
    assert result.merged.get("FOO") == "first"


def test_dedup_cross_merged_contains_all_unique_keys():
    a = make_env({"FOO": "1", "SHARED": "a"})
    b = make_env({"BAR": "2", "SHARED": "b"})
    result = dedup_cross([("a", a), ("b", b)])
    keys = result.merged.keys()
    assert "FOO" in keys
    assert "BAR" in keys
    assert "SHARED" in keys
    assert len(keys) == 3


def test_invalid_keep_raises():
    a = make_env({"X": "1"})
    with pytest.raises(ValueError, match="keep must be"):
        dedup_cross([("a", a)], keep="middle")


def test_cross_dupe_str():
    dupe = CrossFileDupe(key="TOKEN", occurrences=[("dev", "abc"), ("prod", "xyz")])
    s = str(dupe)
    assert "TOKEN" in s
    assert "dev" in s
    assert "prod" in s


def test_multiple_duplicates_detected():
    a = make_env({"A": "1", "B": "x"})
    b = make_env({"A": "2", "B": "y", "C": "3"})
    dupes = find_cross_duplicates([("a", a), ("b", b)])
    dupe_keys = {d.key for d in dupes}
    assert dupe_keys == {"A", "B"}
