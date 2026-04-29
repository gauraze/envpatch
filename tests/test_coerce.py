import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.coerce import coerce_env, CoerceResult


def make_env(**kwargs) -> EnvFile:
    entries = [EnvEntry(key=k, value=v) for k, v in kwargs.items()]
    return EnvFile(entries=entries)


def test_bool_true_variants_normalised():
    env = make_env(ENABLED="yes", ACTIVE="1", FLAG="on")
    result = coerce_env(env, {"ENABLED": "bool", "ACTIVE": "bool", "FLAG": "bool"})
    values = {e.key: e.value for e in result.entries.entries}
    assert values["ENABLED"] == "true"
    assert values["ACTIVE"] == "true"
    assert values["FLAG"] == "true"
    assert len(result.issues) == 3


def test_bool_false_variants_normalised():
    env = make_env(DISABLED="no", OFF="0")
    result = coerce_env(env, {"DISABLED": "bool", "OFF": "bool"})
    values = {e.key: e.value for e in result.entries.entries}
    assert values["DISABLED"] == "false"
    assert values["OFF"] == "false"


def test_already_normalised_bool_no_issue():
    env = make_env(FLAG="true")
    result = coerce_env(env, {"FLAG": "bool"})
    assert result.clean
    assert len(result.issues) == 0


def test_int_coercion_strips_whitespace():
    env = make_env(PORT=" 8080 ")
    result = coerce_env(env, {"PORT": "int"})
    values = {e.key: e.value for e in result.entries.entries}
    assert values["PORT"] == "8080"
    assert len(result.issues) == 1
    assert result.issues[0].coerce_type == "int"


def test_float_coercion():
    env = make_env(RATIO="1")
    result = coerce_env(env, {"RATIO": "float"})
    values = {e.key: e.value for e in result.entries.entries}
    assert values["RATIO"] == "1.0"


def test_str_coercion_strips_whitespace():
    env = make_env(NAME="  hello  ")
    result = coerce_env(env, {"NAME": "str"})
    values = {e.key: e.value for e in result.entries.entries}
    assert values["NAME"] == "hello"


def test_keys_not_in_rules_untouched():
    env = make_env(SECRET="abc", PORT="8080")
    result = coerce_env(env, {"PORT": "int"})
    values = {e.key: e.value for e in result.entries.entries}
    assert values["SECRET"] == "abc"


def test_clean_property_true_when_no_changes():
    env = make_env(PORT="8080")
    result = coerce_env(env, {"PORT": "int"})
    assert result.clean


def test_to_dotenv_output():
    env = make_env(FLAG="yes", PORT="8080")
    result = coerce_env(env, {"FLAG": "bool", "PORT": "int"})
    output = result.to_dotenv()
    assert "FLAG=true" in output
    assert "PORT=8080" in output


def test_issue_str_representation():
    env = make_env(ENABLED="yes")
    result = coerce_env(env, {"ENABLED": "bool"})
    assert str(result.issues[0]) == "ENABLED: 'yes' -> 'true' (as bool)"
