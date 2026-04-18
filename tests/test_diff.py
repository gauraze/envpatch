"""Tests for envpatch.diff."""
from pathlib import Path

import pytest

from envpatch.diff import ChangeType, diff_env_files
from envpatch.parser import parse_env_file


def make_env(tmp_path: Path, name: str, content: str):
    p = tmp_path / name
    p.write_text(content)
    return parse_env_file(p)


def test_added_key(tmp_path):
    base = make_env(tmp_path, "base.env", "FOO=bar\n")
    target = make_env(tmp_path, "target.env", "FOO=bar\nNEW_KEY=hello\n")
    diffs = diff_env_files(base, target)
    added = [d for d in diffs if d.change == ChangeType.ADDED]
    assert len(added) == 1
    assert added[0].key == "NEW_KEY"
    assert added[0].new_value == "hello"


def test_removed_key(tmp_path):
    base = make_env(tmp_path, "base.env", "FOO=bar\nOLD=gone\n")
    target = make_env(tmp_path, "target.env", "FOO=bar\n")
    diffs = diff_env_files(base, target)
    removed = [d for d in diffs if d.change == ChangeType.REMOVED]
    assert len(removed) == 1
    assert removed[0].key == "OLD"


def test_modified_key(tmp_path):
    base = make_env(tmp_path, "base.env", "FOO=old\n")
    target = make_env(tmp_path, "target.env", "FOO=new\n")
    diffs = diff_env_files(base, target)
    assert diffs[0].change == ChangeType.MODIFIED
    assert diffs[0].old_value == "old"
    assert diffs[0].new_value == "new"


def test_unchanged_excluded_by_default(tmp_path):
    base = make_env(tmp_path, "base.env", "FOO=same\n")
    target = make_env(tmp_path, "target.env", "FOO=same\n")
    diffs = diff_env_files(base, target)
    assert diffs == []


def test_unchanged_included_when_flag_set(tmp_path):
    base = make_env(tmp_path, "base.env", "FOO=same\n")
    target = make_env(tmp_path, "target.env", "FOO=same\n")
    diffs = diff_env_files(base, target, include_unchanged=True)
    assert len(diffs) == 1
    assert diffs[0].change == ChangeType.UNCHANGED
