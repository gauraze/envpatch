import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.pin import pin_keys, apply_pins, PinViolation


def make_env(pairs):
    entries = [EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_no_violations_when_values_match():
    env = make_env({"APP_ENV": "production", "DEBUG": "false"})
    result = pin_keys(env, {"APP_ENV": "production"})
    assert result.clean
    assert result.violations == []


def test_violation_when_value_differs():
    env = make_env({"APP_ENV": "staging"})
    result = pin_keys(env, {"APP_ENV": "production"})
    assert not result.clean
    assert len(result.violations) == 1
    v = result.violations[0]
    assert v.key == "APP_ENV"
    assert v.pinned_value == "production"
    assert v.actual_value == "staging"


def test_violation_when_key_missing():
    env = make_env({"DEBUG": "false"})
    result = pin_keys(env, {"APP_ENV": "production"})
    assert not result.clean
    assert result.violations[0].actual_value == "<missing>"


def test_multiple_pins_partial_violation():
    env = make_env({"APP_ENV": "production", "DEBUG": "true"})
    result = pin_keys(env, {"APP_ENV": "production", "DEBUG": "false"})
    assert not result.clean
    assert len(result.violations) == 1
    assert result.violations[0].key == "DEBUG"


def test_apply_pins_overwrites_value():
    env = make_env({"APP_ENV": "staging", "PORT": "8080"})
    updated = apply_pins(env, {"APP_ENV": "production"})
    assert updated.get("APP_ENV") == "production"
    assert updated.get("PORT") == "8080"


def test_apply_pins_adds_missing_key():
    env = make_env({"PORT": "8080"})
    updated = apply_pins(env, {"APP_ENV": "production"})
    assert updated.get("APP_ENV") == "production"


def test_str_violation():
    v = PinViolation("KEY", "expected", "actual")
    assert "KEY" in str(v)
    assert "expected" in str(v)
    assert "actual" in str(v)
