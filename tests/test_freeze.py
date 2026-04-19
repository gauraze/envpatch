import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.freeze import freeze_env, check_freeze, FreezeViolation


def make_env(pairs):
    entries = [EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(entries=entries)


def test_freeze_all_keys():
    env = make_env([("A", "1"), ("B", "2")])
    frozen = freeze_env(env)
    assert frozen == {"A": "1", "B": "2"}


def test_freeze_subset_of_keys():
    env = make_env([("A", "1"), ("B", "2"), ("C", "3")])
    frozen = freeze_env(env, keys=["A", "C"])
    assert frozen == {"A": "1", "C": "3"}
    assert "B" not in frozen


def test_check_freeze_clean():
    env = make_env([("A", "1"), ("B", "2")])
    frozen = {"A": "1", "B": "2"}
    result = check_freeze(env, frozen)
    assert result.clean
    assert result.violations == []


def test_check_freeze_value_changed():
    env = make_env([("A", "new"), ("B", "2")])
    frozen = {"A": "old", "B": "2"}
    result = check_freeze(env, frozen)
    assert not result.clean
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.key == "A"
    assert v.expected == "old"
    assert v.actual == "new"


def test_check_freeze_missing_key():
    env = make_env([("B", "2")])
    frozen = {"A": "1", "B": "2"}
    result = check_freeze(env, frozen)
    assert not result.clean
    assert result.violations[0].key == "A"
    assert result.violations[0].actual is None


def test_violation_str_missing():
    v = FreezeViolation(key="X", expected="val", actual=None)
    assert "missing" in str(v)


def test_violation_str_changed():
    v = FreezeViolation(key="X", expected="old", actual="new")
    assert "old" in str(v)
    assert "new" in str(v)
