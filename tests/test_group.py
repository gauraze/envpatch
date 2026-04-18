import pytest
from envpatch.parser import EnvFile
from envpatch.group import group_by_prefix, group_by_keys, to_grouped_dotenv, GroupResult


def make_env(pairs: dict) -> EnvFile:
    text = "\n".join(f"{k}={v}" for k, v in pairs.items())
    return EnvFile.parse(text)


def test_group_by_prefix_basic():
    env = make_env({"DB_HOST": "localhost", "DB_PORT": "5432", "APP_NAME": "myapp"})
    result = group_by_prefix(env)
    assert "DB" in result.groups
    assert "APP" in result.groups
    assert set(result.groups["DB"]) == {"DB_HOST", "DB_PORT"}
    assert result.groups["APP"] == ["APP_NAME"]


def test_group_by_prefix_ungrouped():
    env = make_env({"HOST": "localhost", "DB_PORT": "5432"})
    result = group_by_prefix(env)
    assert "HOST" in result.ungrouped
    assert "DB_PORT" in result.groups.get("DB", [])


def test_group_by_prefix_custom_sep():
    env = make_env({"DB.HOST": "localhost", "DB.PORT": "5432"})
    result = group_by_prefix(env, sep=".")
    assert "DB" in result.groups
    assert len(result.groups["DB"]) == 2


def test_group_by_keys_explicit():
    env = make_env({"DB_HOST": "h", "DB_PORT": "5432", "SECRET": "x"})
    mapping = {"database": ["DB_HOST", "DB_PORT"], "secrets": ["SECRET"]}
    result = group_by_keys(env, mapping)
    assert "database" in result.groups
    assert "secrets" in result.groups
    assert result.ungrouped == []


def test_group_by_keys_missing_key_skipped():
    env = make_env({"DB_HOST": "h"})
    mapping = {"database": ["DB_HOST", "DB_MISSING"]}
    result = group_by_keys(env, mapping)
    assert result.groups["database"] == ["DB_HOST"]


def test_group_by_keys_ungrouped_remainder():
    env = make_env({"DB_HOST": "h", "EXTRA": "val"})
    mapping = {"database": ["DB_HOST"]}
    result = group_by_keys(env, mapping)
    assert "EXTRA" in result.ungrouped


def test_all_keys_returns_everything():
    env = make_env({"DB_HOST": "h", "APP_NAME": "x", "SOLO": "y"})
    result = group_by_prefix(env)
    all_keys = result.all_keys()
    assert set(all_keys) == {"DB_HOST", "APP_NAME", "SOLO"}


def test_to_grouped_dotenv_format():
    env = make_env({"DB_HOST": "localhost", "APP_NAME": "myapp"})
    result = group_by_prefix(env)
    output = to_grouped_dotenv(env, result)
    assert "# [DB]" in output or "# [APP]" in output
    assert "DB_HOST=localhost" in output
    assert "APP_NAME=myapp" in output
