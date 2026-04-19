import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.filter import filter_keys, to_filtered_dotenv


def make_env(pairs):
    entries = [EnvEntry(key=k, raw_value=v) for k, v in pairs]
    return EnvFile(entries=entries)


def test_filter_by_prefix():
    env = make_env([("DB_HOST", "localhost"), ("DB_PORT", "5432"), ("APP_NAME", "myapp")])
    result = filter_keys(env, prefixes=["DB_"])
    assert [e.key for e in result.matched] == ["DB_HOST", "DB_PORT"]
    assert [e.key for e in result.excluded] == ["APP_NAME"]


def test_filter_by_suffix():
    env = make_env([("DB_HOST", "x"), ("REDIS_HOST", "y"), ("APP_PORT", "z")])
    result = filter_keys(env, suffixes=["_HOST"])
    assert {e.key for e in result.matched} == {"DB_HOST", "REDIS_HOST"}


def test_filter_by_contains():
    env = make_env([("AWS_SECRET_KEY", "x"), ("AWS_ID", "y"), ("PORT", "z")])
    result = filter_keys(env, contains="SECRET")
    assert [e.key for e in result.matched] == ["AWS_SECRET_KEY"]


def test_filter_by_exact_keys():
    env = make_env([("A", "1"), ("B", "2"), ("C", "3")])
    result = filter_keys(env, keys=["A", "C"])
    assert [e.key for e in result.matched] == ["A", "C"]
    assert [e.key for e in result.excluded] == ["B"]


def test_filter_invert():
    env = make_env([("DB_HOST", "x"), ("APP_NAME", "y")])
    result = filter_keys(env, prefixes=["DB_"], invert=True)
    assert [e.key for e in result.matched] == ["APP_NAME"]
    assert [e.key for e in result.excluded] == ["DB_HOST"]


def test_filter_no_criteria_matches_nothing():
    env = make_env([("A", "1"), ("B", "2")])
    result = filter_keys(env)
    assert result.matched == []
    assert len(result.excluded) == 2


def test_to_filtered_dotenv():
    env = make_env([("KEY1", "val1"), ("KEY2", "val2"), ("OTHER", "x")])
    result = filter_keys(env, keys=["KEY1", "KEY2"])
    out = to_filtered_dotenv(result)
    assert "KEY1=val1" in out
    assert "KEY2=val2" in out
    assert "OTHER" not in out


def test_filter_multiple_criteria_union():
    env = make_env([("DB_HOST", "x"), ("APP_SECRET", "y"), ("PORT", "z")])
    result = filter_keys(env, prefixes=["DB_"], contains="SECRET")
    keys = {e.key for e in result.matched}
    assert keys == {"DB_HOST", "APP_SECRET"}
