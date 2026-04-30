"""Tests for envpatch.pivot."""
import pytest

from envpatch.parser import EnvFile, EnvEntry
from envpatch.pivot import pivot_envs, PivotResult


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_pivot_single_file():
    env = make_env({"A": "1", "B": "2"})
    result = pivot_envs([env], labels=["dev"])
    assert result.labels == ["dev"]
    assert result.rows["A"] == ["1"]
    assert result.rows["B"] == ["2"]


def test_pivot_two_files_all_present():
    dev = make_env({"A": "1", "B": "2"})
    prod = make_env({"A": "10", "B": "20"})
    result = pivot_envs([dev, prod], labels=["dev", "prod"])
    assert result.rows["A"] == ["1", "10"]
    assert result.rows["B"] == ["2", "20"]
    assert result.clean is True


def test_pivot_missing_key_in_second_file():
    dev = make_env({"A": "1", "B": "2"})
    prod = make_env({"A": "10"})
    result = pivot_envs([dev, prod], labels=["dev", "prod"])
    assert result.rows["B"] == ["2", None]
    assert result.clean is False


def test_pivot_extra_key_in_second_file():
    dev = make_env({"A": "1"})
    prod = make_env({"A": "10", "C": "30"})
    result = pivot_envs([dev, prod], labels=["dev", "prod"])
    assert result.rows["C"] == [None, "30"]


def test_pivot_default_labels():
    dev = make_env({"X": "1"})
    prod = make_env({"X": "2"})
    result = pivot_envs([dev, prod])
    assert result.labels == ["file_0", "file_1"]


def test_pivot_label_mismatch_raises():
    env = make_env({"A": "1"})
    with pytest.raises(ValueError, match="labels length"):
        pivot_envs([env], labels=["dev", "prod"])


def test_to_table_header():
    dev = make_env({"A": "1"})
    prod = make_env({"A": "2"})
    result = pivot_envs([dev, prod], labels=["dev", "prod"])
    table = result.to_table()
    assert table[0] == ["KEY", "dev", "prod"]


def test_to_table_missing_marker():
    dev = make_env({"A": "1", "B": "2"})
    prod = make_env({"A": "10"})
    result = pivot_envs([dev, prod], labels=["dev", "prod"], missing_marker="N/A")
    table = result.to_table()
    b_row = next(r for r in table if r[0] == "B")
    assert b_row[2] == "N/A"


def test_keys_sorted():
    env = make_env({"Z": "1", "A": "2", "M": "3"})
    result = pivot_envs([env])
    assert result.keys() == ["A", "M", "Z"]
