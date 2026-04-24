"""Tests for envpatch.resolve."""
from __future__ import annotations

from envpatch.parser import EnvFile, EnvEntry
from envpatch.resolve import resolve_env


def make_env(**kwargs: str) -> EnvFile:
    entries = [EnvEntry(key=k, value=v) for k, v in kwargs.items()]
    return EnvFile(entries=entries)


def test_resolve_fills_empty_value_from_fallback():
    base = make_env(FOO="", BAR="kept")
    fb = make_env(FOO="from_fb", BAR="ignored")
    result = resolve_env(base, [fb])
    values = {e.key: e.value for e in result.entries}
    assert values["FOO"] == "from_fb"
    assert values["BAR"] == "kept"
    assert len(result.resolved) == 1
    assert result.resolved[0].key == "FOO"


def test_resolve_adds_key_missing_from_base():
    base = make_env(FOO="hello")
    fb = make_env(FOO="world", NEW_KEY="added")
    result = resolve_env(base, [fb])
    keys = [e.key for e in result.entries]
    assert "NEW_KEY" in keys
    assert len(result.resolved) == 1


def test_resolve_does_not_overwrite_by_default():
    base = make_env(FOO="original")
    fb = make_env(FOO="replacement")
    result = resolve_env(base, [fb])
    values = {e.key: e.value for e in result.entries}
    assert values["FOO"] == "original"
    assert len(result.resolved) == 0


def test_resolve_overwrite_flag_replaces_value():
    base = make_env(FOO="original")
    fb = make_env(FOO="replacement")
    result = resolve_env(base, [fb], overwrite=True)
    values = {e.key: e.value for e in result.entries}
    assert values["FOO"] == "replacement"
    assert len(result.resolved) == 1


def test_resolve_unresolved_when_no_fallback_has_value():
    base = make_env(FOO="", BAR="")
    fb = make_env(FOO="from_fb")
    result = resolve_env(base, [fb])
    assert "BAR" in result.unresolved
    assert "FOO" not in result.unresolved
    assert not result.clean


def test_resolve_clean_when_all_resolved():
    base = make_env(FOO="", BAR="")
    fb = make_env(FOO="a", BAR="b")
    result = resolve_env(base, [fb])
    assert result.clean
    assert len(result.unresolved) == 0


def test_resolve_explicit_keys_only():
    base = make_env(FOO="", BAR="")
    fb = make_env(FOO="a", BAR="b")
    result = resolve_env(base, [fb], keys=["FOO"])
    values = {e.key: e.value for e in result.entries}
    assert values["FOO"] == "a"
    assert values["BAR"] == ""


def test_resolve_first_fallback_wins():
    base = make_env(FOO="")
    fb1 = make_env(FOO="first")
    fb2 = make_env(FOO="second")
    result = resolve_env(base, [fb1, fb2])
    values = {e.key: e.value for e in result.entries}
    assert values["FOO"] == "first"


def test_resolve_to_dotenv_format():
    base = make_env(FOO="", BAR="baz")
    fb = make_env(FOO="filled")
    result = resolve_env(base, [fb])
    dotenv = result.to_dotenv()
    assert "FOO=filled" in dotenv
    assert "BAR=baz" in dotenv
