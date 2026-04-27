from __future__ import annotations

import pytest

from envpatch.parser import EnvFile
from envpatch.truncate import truncate_env, TruncateResult


def make_env(pairs: dict) -> EnvFile:
    text = "\n".join(f"{k}={v}" for k, v in pairs.items())
    return EnvFile.parse(text)


def test_truncate_long_value_is_cut():
    env = make_env({"SECRET": "a" * 50})
    result = truncate_env(env, max_length=10)
    assert result.truncated == {"SECRET": 50}
    entry = next(e for e in result.entries if e.key == "SECRET")
    assert entry.value == "a" * 10


def test_short_value_unchanged():
    env = make_env({"KEY": "short"})
    result = truncate_env(env, max_length=20)
    assert result.clean is True
    assert result.truncated == {}
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.value == "short"


def test_suffix_appended_to_truncated_value():
    env = make_env({"MSG": "hello world this is long"})
    result = truncate_env(env, max_length=10, suffix="...")
    entry = next(e for e in result.entries if e.key == "MSG")
    assert entry.value == "hello w..."
    assert len(entry.value) == 10


def test_truncate_only_specified_keys():
    env = make_env({"A": "a" * 30, "B": "b" * 30})
    result = truncate_env(env, max_length=5, keys=["A"])
    assert "A" in result.truncated
    assert "B" not in result.truncated
    b_entry = next(e for e in result.entries if e.key == "B")
    assert b_entry.value == "b" * 30


def test_clean_flag_false_when_truncated():
    env = make_env({"X": "x" * 100})
    result = truncate_env(env, max_length=10)
    assert result.clean is False


def test_to_dotenv_serialises_correctly():
    env = make_env({"LONG": "a" * 20, "SHORT": "hi"})
    result = truncate_env(env, max_length=5)
    dotenv = result.to_dotenv()
    reparsed = EnvFile.parse(dotenv)
    assert reparsed.get("LONG") == "a" * 5
    assert reparsed.get("SHORT") == "hi"


def test_suffix_longer_than_max_raises():
    env = make_env({"K": "value"})
    with pytest.raises(ValueError, match="max_length"):
        truncate_env(env, max_length=2, suffix="...")


def test_exact_length_value_not_truncated():
    env = make_env({"K": "12345"})
    result = truncate_env(env, max_length=5)
    assert result.clean is True
