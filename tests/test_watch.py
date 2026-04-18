"""Tests for envpatch.watch."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from envpatch.watch import watch_env_file, WatchEvent


def test_watch_event_has_changes_false():
    event = WatchEvent(path=Path(".env"), changes=[])
    assert not event.has_changes()


def test_watch_event_has_changes_true():
    from envpatch.diff import DiffEntry, ChangeType
    entry = DiffEntry(key="FOO", change_type=ChangeType.ADDED, new_value="bar")
    event = WatchEvent(path=Path(".env"), changes=[entry])
    assert event.has_changes()


def test_watch_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        watch_env_file(tmp_path / "missing.env", callback=lambda e: None, max_iterations=0)


def test_watch_detects_added_key(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n")

    events: list[WatchEvent] = []

    def _write_and_wait():
        time.sleep(0.05)
        env_file.write_text("FOO=bar\nNEW=value\n")

    import threading
    t = threading.Thread(target=_write_and_wait, daemon=True)
    t.start()

    watch_env_file(env_file, callback=events.append, interval=0.02, max_iterations=10)
    t.join()

    assert any(e.has_changes() for e in events)
    keys = {c.key for e in events for c in e.changes}
    assert "NEW" in keys


def test_watch_no_change_no_callback(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n")

    events: list[WatchEvent] = []
    watch_env_file(env_file, callback=events.append, interval=0.01, max_iterations=3)
    assert events == []
