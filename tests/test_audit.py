"""Tests for envpatch.audit module."""
import json
import os
import pytest
from envpatch.audit import (
    AuditLog, AuditEntry, save_audit, load_audit, append_audit, AUDIT_VERSION
)


def test_add_entry():
    log = AuditLog()
    entry = log.add(action="patch", target=".env", keys_changed=["FOO", "BAR"])
    assert len(log.entries) == 1
    assert entry.action == "patch"
    assert entry.keys_changed == ["FOO", "BAR"]
    assert entry.timestamp  # non-empty


def test_save_and_load_roundtrip(tmp_path):
    path = str(tmp_path / "audit.json")
    log = AuditLog()
    log.add(action="merge", target=".env.prod", keys_changed=["DB_URL"], source=".env.base")
    save_audit(log, path)
    loaded = load_audit(path)
    assert loaded.version == AUDIT_VERSION
    assert len(loaded.entries) == 1
    e = loaded.entries[0]
    assert e.action == "merge"
    assert e.source == ".env.base"
    assert e.target == ".env.prod"


def test_load_missing_file(tmp_path):
    path = str(tmp_path / "nonexistent.json")
    log = load_audit(path)
    assert log.entries == []


def test_load_bad_version(tmp_path):
    path = str(tmp_path / "audit.json")
    with open(path, "w") as fh:
        json.dump({"version": 99, "entries": []}, fh)
    with pytest.raises(ValueError, match="Unsupported"):
        load_audit(path)


def test_append_audit_creates_and_accumulates(tmp_path):
    path = str(tmp_path / "audit.json")
    append_audit(path, action="patch", target=".env", keys_changed=["X"])
    append_audit(path, action="snapshot", target=".env", keys_changed=["Y"], note="backup")
    log = load_audit(path)
    assert len(log.entries) == 2
    assert log.entries[1].note == "backup"
    assert log.entries[1].action == "snapshot"


def test_entry_note_optional():
    log = AuditLog()
    entry = log.add(action="patch", target=".env", keys_changed=[])
    assert entry.note is None
    assert entry.source is None
