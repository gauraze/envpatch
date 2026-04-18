import pytest
from envpatch.parser import EnvFile
from envpatch.promote import promote_keys, PromoteResult


def make_env(data: dict) -> EnvFile:
    return EnvFile(data=data, comments={})


def test_promote_new_key():
    src = make_env({"NEW_KEY": "hello", "SHARED": "same"})
    tgt = make_env({"SHARED": "same"})
    updated, result = promote_keys(src, tgt)
    assert updated.data["NEW_KEY"] == "hello"
    assert "NEW_KEY" in result.promoted


def test_promote_conflict_no_overwrite():
    src = make_env({"KEY": "new_val"})
    tgt = make_env({"KEY": "old_val"})
    updated, result = promote_keys(src, tgt, overwrite=False)
    assert updated.data["KEY"] == "old_val"
    assert "KEY" in result.conflicts
    assert "KEY" in result.skipped
    assert "KEY" not in result.promoted


def test_promote_conflict_with_overwrite():
    src = make_env({"KEY": "new_val"})
    tgt = make_env({"KEY": "old_val"})
    updated, result = promote_keys(src, tgt, overwrite=True)
    assert updated.data["KEY"] == "new_val"
    assert "KEY" in result.promoted
    assert "KEY" in result.conflicts


def test_promote_subset_of_keys():
    src = make_env({"A": "1", "B": "2", "C": "3"})
    tgt = make_env({})
    updated, result = promote_keys(src, tgt, keys=["A", "C"])
    assert "A" in updated.data
    assert "C" in updated.data
    assert "B" not in updated.data
    assert result.promoted == ["A", "C"]


def test_promote_missing_key_in_source_skipped():
    src = make_env({"A": "1"})
    tgt = make_env({})
    updated, result = promote_keys(src, tgt, keys=["A", "MISSING"])
    assert "MISSING" in result.skipped
    assert "MISSING" not in updated.data


def test_clean_result_when_no_conflicts():
    src = make_env({"X": "val"})
    tgt = make_env({})
    _, result = promote_keys(src, tgt)
    assert result.clean is True


def test_not_clean_when_conflicts():
    src = make_env({"X": "new"})
    tgt = make_env({"X": "old"})
    _, result = promote_keys(src, tgt, overwrite=False)
    assert result.clean is False
