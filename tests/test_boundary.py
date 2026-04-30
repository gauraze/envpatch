"""Tests for envpatch.boundary."""
import pytest

from envpatch.parser import EnvFile, EnvEntry
from envpatch.boundary import check_boundaries, BoundaryViolation


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_no_constraints_always_clean():
    env = make_env({"APP_HOST": "localhost", "DB_PORT": "5432"})
    result = check_boundaries(env)
    assert result.clean
    assert result.checked == 2


def test_allowed_prefix_passes():
    env = make_env({"APP_HOST": "localhost", "APP_PORT": "8080"})
    result = check_boundaries(env, allowed_prefixes=["APP_"])
    assert result.clean


def test_allowed_prefix_violation():
    env = make_env({"APP_HOST": "localhost", "DB_PORT": "5432"})
    result = check_boundaries(env, allowed_prefixes=["APP_"])
    assert not result.clean
    assert len(result.violations) == 1
    assert result.violations[0].key == "DB_PORT"


def test_allowed_suffix_passes():
    env = make_env({"APP_URL": "http://x", "DB_URL": "postgres://y"})
    result = check_boundaries(env, allowed_suffixes=["_URL"])
    assert result.clean


def test_allowed_suffix_violation():
    env = make_env({"APP_URL": "http://x", "APP_HOST": "localhost"})
    result = check_boundaries(env, allowed_suffixes=["_URL"])
    assert not result.clean
    assert result.violations[0].key == "APP_HOST"


def test_denied_prefix_violation():
    env = make_env({"INTERNAL_SECRET": "abc", "APP_KEY": "xyz"})
    result = check_boundaries(env, denied_prefixes=["INTERNAL_"])
    assert not result.clean
    keys = [v.key for v in result.violations]
    assert "INTERNAL_SECRET" in keys
    assert "APP_KEY" not in keys


def test_denied_suffix_violation():
    env = make_env({"DB_SECRET": "s3cr3t", "DB_HOST": "localhost"})
    result = check_boundaries(env, denied_suffixes=["_SECRET"])
    assert not result.clean
    assert result.violations[0].key == "DB_SECRET"


def test_violation_str():
    v = BoundaryViolation(key="BAD_KEY", reason="starts with denied prefix: 'BAD_'")
    assert "BAD_KEY" in str(v)
    assert "denied prefix" in str(v)


def test_multiple_violations_counted():
    env = make_env({"X_ONE": "1", "X_TWO": "2", "APP_THREE": "3"})
    result = check_boundaries(env, allowed_prefixes=["APP_"])
    assert len(result.violations) == 2
    assert result.checked == 3


def test_empty_env_is_clean():
    env = make_env({})
    result = check_boundaries(env, allowed_prefixes=["APP_"], denied_suffixes=["_TMP"])
    assert result.clean
    assert result.checked == 0
