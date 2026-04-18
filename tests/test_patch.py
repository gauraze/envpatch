"""Tests for envpatch.patch module."""

import pytest
from envpatch.parser import EnvFile
from envpatch.diff import DiffEntry, ChangeType, diff_env_files
from envpatch.patch import apply_patch


def make_env(content: str) -> EnvFile:
    return EnvFile.from_string(content)


def test_apply_added_key():
    base = make_env("FOO=bar\n")
    changes = [DiffEntry(ChangeType.ADDED, "NEW_KEY", None, "hello")]
    patched = apply_patch(base, changes, dry_run=True)
    assert patched.get("NEW_KEY") == "hello"
    assert patched.get("FOO") == "bar"


def test_apply_removed_key():
    base = make_env("FOO=bar\nBAZ=qux\n")
    changes = [DiffEntry(ChangeType.REMOVED, "FOO", "bar", None)]
    patched = apply_patch(base, changes, dry_run=True)
    assert patched.get("FOO") is None
    assert patched.get("BAZ") == "qux"


def test_apply_modified_key():
    base = make_env("FOO=old\nBAR=keep\n")
    changes = [DiffEntry(ChangeType.MODIFIED, "FOO", "old", "new")]
    patched = apply_patch(base, changes, dry_run=True)
    assert patched.get("FOO") == "new"
    assert patched.get("BAR") == "keep"


def test_apply_multiple_changes():
    base = make_env("A=1\nB=2\nC=3\n")
    changes = [
        DiffEntry(ChangeType.MODIFIED, "A", "1", "10"),
        DiffEntry(ChangeType.REMOVED, "B", "2", None),
        DiffEntry(ChangeType.ADDED, "D", None, "4"),
    ]
    patched = apply_patch(base, changes, dry_run=True)
    assert patched.get("A") == "10"
    assert patched.get("B") is None
    assert patched.get("C") == "3"
    assert patched.get("D") == "4"


def test_roundtrip_via_diff():
    source = make_env("X=1\nY=2\n")
    target = make_env("X=99\nZ=3\n")
    changes = [e for e in diff_env_files(source, target) if e.change_type != ChangeType.UNCHANGED]
    patched = apply_patch(source, changes, dry_run=True)
    assert patched.get("X") == "99"
    assert patched.get("Z") == "3"
