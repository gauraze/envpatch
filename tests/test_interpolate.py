"""Tests for envpatch.interpolate."""
import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.interpolate import interpolate


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_no_references_unchanged():
    env = make_env({"HOST": "localhost", "PORT": "5432"})
    result = interpolate(env)
    assert result.entries["HOST"] == "localhost"
    assert result.entries["PORT"] == "5432"
    assert result.clean


def test_curly_brace_reference_resolved():
    env = make_env({"BASE": "http://example.com", "URL": "${BASE}/api"})
    result = interpolate(env)
    assert result.entries["URL"] == "http://example.com/api"
    assert result.clean


def test_bare_dollar_reference_resolved():
    env = make_env({"HOST": "db", "DSN": "postgres://$HOST/mydb"})
    result = interpolate(env)
    assert result.entries["DSN"] == "postgres://db/mydb"
    assert result.clean


def test_chained_references_resolved():
    env = make_env({"A": "hello", "B": "${A}_world", "C": "${B}!"})
    result = interpolate(env)
    assert result.entries["C"] == "hello_world!"
    assert result.clean


def test_unresolved_reference_reported():
    env = make_env({"URL": "${MISSING}/path"})
    result = interpolate(env)
    assert "MISSING" in result.unresolved
    assert not result.clean
    assert "${MISSING}" in result.entries["URL"]


def test_extra_context_used():
    env = make_env({"URL": "${DOMAIN}/api"})
    result = interpolate(env, extra={"DOMAIN": "example.com"})
    assert result.entries["URL"] == "example.com/api"
    assert result.clean


def test_self_reference_does_not_loop():
    env = make_env({"A": "${A}"})
    result = interpolate(env)
    assert "A" in result.unresolved
    assert not result.clean


def test_multiple_references_in_one_value():
    env = make_env({"HOST": "localhost", "PORT": "5432", "DSN": "${HOST}:${PORT}"})
    result = interpolate(env)
    assert result.entries["DSN"] == "localhost:5432"
    assert result.clean
