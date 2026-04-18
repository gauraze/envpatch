"""Tests for envpatch.snapshot."""
import json
import os
import pytest

from envpatch.parser import EnvEntry, EnvFile
from envpatch.snapshot import save_snapshot, load_snapshot, snapshot_metadata


def make_env(*pairs):
    entries = [EnvEntry(key=k, value=v) for k, v in pairs]
    return EnvFile(entries=entries)


def test_save_creates_file(tmp_path):
    env = make_env(("FOO", "bar"), ("BAZ", "qux"))
    out = str(tmp_path / "snap.json")
    save_snapshot(env, out, label="test")
    assert os.path.exists(out)


def test_save_structure(tmp_path):
    env = make_env(("KEY", "val"))
    out = str(tmp_path / "snap.json")
    data = save_snapshot(env, out, label="mylabel")
    assert data["version"] == 1
    assert data["label"] == "mylabel"
    assert "created_at" in data
    assert data["entries"] == [{"key": "KEY", "value": "val", "comment": None}]


def test_roundtrip(tmp_path):
    env = make_env(("A", "1"), ("B", "2"), ("C", "3"))
    out = str(tmp_path / "snap.json")
    save_snapshot(env, out)
    loaded = load_snapshot(out)
    assert loaded.keys() == env.keys()
    assert loaded.get("A") == "1"
    assert loaded.get("C") == "3"


def test_load_bad_version(tmp_path):
    bad = {"version": 99, "label": "x", "created_at": "now", "entries": []}
    out = str(tmp_path / "bad.json")
    with open(out, "w") as fh:
        json.dump(bad, fh)
    with pytest.raises(ValueError, match="Unsupported snapshot version"):
        load_snapshot(out)


def test_snapshot_metadata(tmp_path):
    env = make_env(("X", "1"), ("Y", "2"))
    out = str(tmp_path / "snap.json")
    save_snapshot(env, out, label="prod")
    meta = snapshot_metadata(out)
    assert meta["label"] == "prod"
    assert meta["entry_count"] == 2
    assert meta["version"] == 1
