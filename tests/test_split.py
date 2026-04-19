import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.split import split_by_prefix, to_split_dotenv, SplitResult


def make_env(pairs):
    entries = [EnvEntry(key=k, value=v) for k, v in pairs]
    return EnvFile(entries=entries)


def test_split_basic_prefix():
    env = make_env([("DB_HOST", "localhost"), ("DB_PORT", "5432"), ("APP_NAME", "myapp")])
    result = split_by_prefix(env, ["DB", "APP"])
    assert len(result.groups["DB"]) == 2
    assert len(result.groups["APP"]) == 1
    assert result.ungrouped == []


def test_split_ungrouped_keys():
    env = make_env([("DB_HOST", "localhost"), ("SECRET", "abc")])
    result = split_by_prefix(env, ["DB"])
    assert len(result.ungrouped) == 1
    assert result.ungrouped[0].key == "SECRET"
    assert not result.clean


def test_split_clean_when_all_grouped():
    env = make_env([("DB_HOST", "localhost")])
    result = split_by_prefix(env, ["DB"])
    assert result.clean


def test_split_strip_prefix():
    env = make_env([("DB_HOST", "localhost"), ("DB_PORT", "5432")])
    result = split_by_prefix(env, ["DB"], keep_prefix=False)
    keys = [e.key for e in result.groups["DB"]]
    assert "HOST" in keys
    assert "PORT" in keys


def test_split_keep_prefix_by_default():
    env = make_env([("DB_HOST", "localhost")])
    result = split_by_prefix(env, ["DB"])
    assert result.groups["DB"][0].key == "DB_HOST"


def test_split_custom_separator():
    env = make_env([("DB.HOST", "localhost"), ("APP.NAME", "x")])
    result = split_by_prefix(env, ["DB", "APP"], sep=".")
    assert len(result.groups["DB"]) == 1
    assert len(result.groups["APP"]) == 1


def test_to_split_dotenv_format():
    entries = [EnvEntry(key="DB_HOST", value="localhost"), EnvEntry(key="DB_PORT", value="5432")]
    out = to_split_dotenv(entries)
    assert "DB_HOST=localhost" in out
    assert "DB_PORT=5432" in out


def test_to_split_dotenv_with_comment():
    entries = [EnvEntry(key="DB_HOST", value="localhost", comment="database host")]
    out = to_split_dotenv(entries)
    assert "# database host" in out
    assert "DB_HOST=localhost" in out
