"""Tests for envpatch.export module."""
import json
import csv
import io

import pytest

from envpatch.diff import DiffEntry, ChangeType
from envpatch.export import to_json, to_csv, to_dotenv_patch


def make_entries():
    return [
        DiffEntry(key="HOST", change_type=ChangeType.UNCHANGED, old_value="localhost", new_value="localhost"),
        DiffEntry(key="PORT", change_type=ChangeType.MODIFIED, old_value="5432", new_value="5433"),
        DiffEntry(key="NEW_KEY", change_type=ChangeType.ADDED, old_value=None, new_value="value1"),
        DiffEntry(key="OLD_KEY", change_type=ChangeType.REMOVED, old_value="old", new_value=None),
    ]


def test_to_json_excludes_unchanged_by_default():
    entries = make_entries()
    result = json.loads(to_json(entries))
    keys = [r["key"] for r in result]
    assert "HOST" not in keys
    assert "PORT" in keys
    assert "NEW_KEY" in keys
    assert "OLD_KEY" in keys


def test_to_json_includes_unchanged_when_requested():
    entries = make_entries()
    result = json.loads(to_json(entries, include_unchanged=True))
    keys = [r["key"] for r in result]
    assert "HOST" in keys


def test_to_json_change_values():
    entries = make_entries()
    result = {r["key"]: r for r in json.loads(to_json(entries))}
    assert result["PORT"]["old_value"] == "5432"
    assert result["PORT"]["new_value"] == "5433"
    assert result["NEW_KEY"]["old_value"] is None


def test_to_csv_headers_and_rows():
    entries = make_entries()
    raw = to_csv(entries)
    reader = csv.DictReader(io.StringIO(raw))
    rows = list(reader)
    assert reader.fieldnames == ["key", "change", "old_value", "new_value"]
    keys = [r["key"] for r in rows]
    assert "HOST" not in keys
    assert "PORT" in keys


def test_to_dotenv_patch_added_and_modified():
    entries = make_entries()
    patch = to_dotenv_patch(entries)
    assert "PORT=5433" in patch
    assert "NEW_KEY=value1" in patch


def test_to_dotenv_patch_removed_commented():
    entries = make_entries()
    patch = to_dotenv_patch(entries)
    assert "# REMOVED: OLD_KEY" in patch


def test_to_dotenv_patch_unchanged_excluded():
    entries = make_entries()
    patch = to_dotenv_patch(entries)
    assert "HOST" not in patch
