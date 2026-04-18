import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.copy import copy_keys, CopyResult


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries)


def test_copy_new_key():
    src = make_env({"NEW_KEY": "hello"})
    tgt = make_env({"EXISTING": "world"})
    updated, result = copy_keys(src, tgt)
    assert "NEW_KEY" in result.copied
    assert updated.get("NEW_KEY").value == "hello"
    assert updated.get("EXISTING").value == "world"


def test_copy_skips_existing_without_overwrite():
    src = make_env({"KEY": "new_val"})
    tgt = make_env({"KEY": "old_val"})
    updated, result = copy_keys(src, tgt)
    assert "KEY" in result.skipped
    assert updated.get("KEY").value == "old_val"


def test_copy_overwrites_when_flag_set():
    src = make_env({"KEY": "new_val"})
    tgt = make_env({"KEY": "old_val"})
    updated, result = copy_keys(src, tgt, overwrite=True)
    assert "KEY" in result.overwritten
    assert updated.get("KEY").value == "new_val"


def test_copy_subset_of_keys():
    src = make_env({"A": "1", "B": "2", "C": "3"})
    tgt = make_env({})
    updated, result = copy_keys(src, tgt, keys=["A", "C"])
    assert set(result.copied) == {"A", "C"}
    assert updated.get("B") is None


def test_copy_missing_key_in_source_ignored():
    src = make_env({"A": "1"})
    tgt = make_env({})
    updated, result = copy_keys(src, tgt, keys=["A", "MISSING"])
    assert "A" in result.copied
    assert "MISSING" not in result.copied


def test_clean_true_when_no_skips():
    src = make_env({"X": "1"})
    tgt = make_env({})
    _, result = copy_keys(src, tgt)
    assert result.clean is True


def test_clean_false_when_skips():
    src = make_env({"X": "1"})
    tgt = make_env({"X": "old"})
    _, result = copy_keys(src, tgt)
    assert result.clean is False
