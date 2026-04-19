"""Tests for envpatch.defaults."""
from __future__ import annotations
import pytest
from envpatch.parser import EnvFile
from envpatch.defaults import apply_defaults, to_defaults_dotenv


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_apply_new_key():
    env = make_env("FOO=bar\n")
    result = apply_defaults(env, {"BAZ": "qux"})
    keys = [e.key for e in result.entries if e.key]
    assert "BAZ" in keys
    assert "FOO" in keys
    assert "BAZ" in result.applied


def test_existing_key_skipped_by_default():
    env = make_env("FOO=bar\n")
    result = apply_defaults(env, {"FOO": "new"})
    assert "FOO" in result.skipped
    assert result.clean  # no keys were applied
    val = next(e.value for e in result.entries if e.key == "FOO")
    assert val == "bar"


def test_existing_key_overwritten_when_flag():
    env = make_env("FOO=bar\n")
    result = apply_defaults(env, {"FOO": "new"}, overwrite=True)
    assert "FOO" in result.applied
    val = next(e.value for e in result.entries if e.key == "FOO")
    assert val == "new"


def test_multiple_defaults_mixed():
    env = make_env("A=1\n")
    result = apply_defaults(env, {"A": "99", "B": "2"})
    assert "A" in result.skipped
    assert "B" in result.applied
    assert not result.clean  # B was applied


def test_clean_flag_true_when_nothing_applied():
    env = make_env("X=1\n")
    result = apply_defaults(env, {"X": "2"})
    assert result.clean


def test_to_defaults_dotenv_output():
    env = make_env("FOO=bar\n")
    result = apply_defaults(env, {"BAZ": "qux"})
    output = to_defaults_dotenv(result)
    assert "FOO=bar" in output
    assert "BAZ=qux" in output


def test_empty_env_gets_defaults():
    env = make_env("")
    result = apply_defaults(env, {"KEY": "val"})
    assert "KEY" in result.applied
    keys = [e.key for e in result.entries if e.key]
    assert "KEY" in keys
