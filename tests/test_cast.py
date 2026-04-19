import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.cast import cast_env, CastResult, CastIssue


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_cast_int_success():
    env = make_env({"PORTn    result = cast_env(env, {"PORT": "int"})
    assert result.values["PORT"] == 8080
    assert isinstance(result.values["PORT"], int)
    assert result.clean


def test_cast_float_success():
    env = make_env({"RATIO": "3.14"})
    result = cast_env(env, {"RATIO": "float"})
    assert abs(result.values["RATIO"] - 3.14) < 1e-9
    assert result.clean


def test_cast_bool_true_variants():
    for val in ("true", "1", "yes"):
        env = make_env({"FLAG": val})
        result = cast_env(env, {"FLAG": "bool"})
        assert result.values["FLAG"] is True
        assert result.clean


def test_cast_bool_false_variants():
    for val in ("false", "0", "no"):
        env = make_env({"FLAG": val})
        result = cast_env(env, {"FLAG": "bool"})
        assert result.values["FLAG"] is False
        assert result.clean


def test_cast_invalid_int_records_issue():
    env = make_env({"PORT": "not-a-number"})
    result = cast_env(env, {"PORT": "int"})
    assert not result.clean
    assert len(result.issues) == 1
    issue = result.issues[0]
    assert issue.key == "PORT"
    assert issue.expected == "int"
    assert "not-a-number" in str(issue)


def test_cast_invalid_bool_records_issue():
    env = make_env({"ENABLED": "maybe"})
    result = cast_env(env, {"ENABLED": "bool"})
    assert not result.clean
    assert result.issues[0].expected == "bool"


def test_unschema_key_returned_as_string():
    env = make_env({"NAME": "alice"})
    result = cast_env(env, {})
    assert result.values["NAME"] == "alice"
    assert result.clean


def test_mixed_schema_partial_failure():
    env = make_env({"PORT": "abc", "HOST": "localhost", "WORKERS": "4"})
    result = cast_env(env, {"PORT": "int", "WORKERS": "int"})
    assert not result.clean
    assert len(result.issues) == 1
    assert result.values["WORKERS"] == 4
    assert result.values["HOST"] == "localhost"
