"""Tests for envpatch.history."""
import pytest
from pathlib import Path
from envpatch.history import (
    record_entry,
    save_history,
    load_history,
    append_history,
    filter_history,
    HistoryEntry,
)


def test_record_entry_fields():
    e = record_entry("dev.env", "staging.env", 3, ["added FOO"], tag="v1")
    assert e.source == "dev.env"
    assert e.target == "staging.env"
    assert e.changes == 3
    assert e.summary == ["added FOO"]
    assert e.tag == "v1"
    assert e.timestamp  # non-empty


def test_save_and_load_roundtrip(tmp_path):
    path = tmp_path / "history.json"
    e = record_entry("a.env", "b.env", 1, ["added X"])
    save_history([e], path)
    loaded = load_history(path)
    assert len(loaded) == 1
    assert loaded[0].source == "a.env"
    assert loaded[0].changes == 1


def test_load_missing_file(tmp_path):
    result = load_history(tmp_path / "missing.json")
    assert result == []


def test_load_bad_version(tmp_path):
    path = tmp_path / "history.json"
    path.write_text('{"version": 99, "entries": []}')
    with pytest.raises(ValueError, match="Unsupported"):
        load_history(path)


def test_append_accumulates(tmp_path):
    path = tmp_path / "history.json"
    append_history(record_entry("a", "b", 1, []), path)
    append_history(record_entry("c", "d", 2, []), path)
    entries = load_history(path)
    assert len(entries) == 2
    assert entries[1].source == "c"


def test_filter_by_source():
    entries = [
        record_entry("dev", "staging", 1, []),
        record_entry("staging", "prod", 2, []),
    ]
    result = filter_history(entries, source="dev")
    assert len(result) == 1
    assert result[0].target == "staging"


def test_filter_by_tag():
    entries = [
        record_entry("a", "b", 1, [], tag="release"),
        record_entry("a", "b", 1, [], tag="hotfix"),
    ]
    result = filter_history(entries, tag="release")
    assert len(result) == 1
    assert result[0].tag == "release"
