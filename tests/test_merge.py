"""Tests for envpatch.merge module."""

import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.merge import merge_env_files, MergeStrategy, MergeConflict


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_merge_adds_keys_from_other():
    base = make_env({"A": "1"})
    other = make_env({"B": "2"})
    result = merge_env_files(base, other)
    assert result.get("A").value == "1"
    assert result.get("B").value == "2"


def test_merge_keeps_base_only_keys():
    base = make_env({"A": "1", "C": "3"})
    other = make_env({"A": "1"})
    result = merge_env_files(base, other)
    assert result.get("C").value == "3"


def test_merge_conflict_theirs_wins_by_default():
    base = make_env({"A": "old"})
    other = make_env({"A": "new"})
    result = merge_env_files(base, other, strategy=MergeStrategy.THEIRS)
    assert result.get("A").value == "new"


def test_merge_conflict_ours_wins():
    base = make_env({"A": "old"})
    other = make_env({"A": "new"})
    result = merge_env_files(base, other, strategy=MergeStrategy.OURS)
    assert result.get("A").value == "old"


def test_merge_no_conflict_same_value():
    base = make_env({"A": "same"})
    other = make_env({"A": "same"})
    result = merge_env_files(base, other)
    assert result.get("A").value == "same"


def test_merge_prompt_strategy_raises_on_conflict():
    base = make_env({"A": "1"})
    other = make_env({"A": "2"})
    with pytest.raises(MergeConflict) as exc_info:
        merge_env_files(base, other, strategy=MergeStrategy.PROMPT)
    assert exc_info.value.key == "A"
    assert exc_info.value.base_val == "1"
    assert exc_info.value.other_val == "2"


def test_merge_preserves_order_base_first():
    base = make_env({"A": "1", "B": "2"})
    other = make_env({"C": "3", "A": "1"})
    result = merge_env_files(base, other)
    keys = [e.key for e in result.entries]
    assert keys.index("A") < keys.index("C")
    assert keys.index("B") < keys.index("C")
