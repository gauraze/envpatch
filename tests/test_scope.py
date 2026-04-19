import pytest
from envpatch.parser import EnvFile
from envpatch.scope import scope_env, to_scoped_dotenv


def make_env(pairs: dict) -> EnvFile:
    text = "\n".join(f"{k}={v}" for k, v in pairs.items())
    return EnvFile.parse(text)


def test_scope_adds_prefix():
    env = make_env({"FOO": "bar", "BAZ": "qux"})
    result = scope_env(env, "APP_")
    assert "APP_FOO" in result.scoped
    assert "APP_BAZ" in result.scoped
    assert result.clean


def test_scope_subset_of_keys():
    env = make_env({"FOO": "1", "BAR": "2", "BAZ": "3"})
    result = scope_env(env, "NS_", keys=["FOO", "BAR"])
    assert "NS_FOO" in result.scoped
    assert "NS_BAR" in result.scoped
    assert "BAZ" in result.skipped
    assert "NS_BAZ" not in result.scoped


def test_scope_skipped_not_clean():
    env = make_env({"A": "1", "B": "2"})
    result = scope_env(env, "P_", keys=["A"])
    assert not result.clean


def test_scope_preserves_values():
    env = make_env({"TOKEN": "abc123"})
    result = scope_env(env, "MY_")
    assert result.scoped["MY_TOKEN"] == "abc123"


def test_strip_prefix_before_apply():
    env = make_env({"APP_KEY": "val"})
    result = scope_env(env, "APP_", strip_prefix=True)
    # APP_ stripped then re-applied → still APP_KEY
    assert "APP_KEY" in result.scoped


def test_to_scoped_dotenv_basic():
    env = make_env({"DB": "postgres"})
    result = scope_env(env, "PROD_")
    out = to_scoped_dotenv(result)
    assert "PROD_DB=postgres" in out


def test_to_scoped_dotenv_quotes_spaces():
    env = make_env({"MSG": "hello world"})
    result = scope_env(env, "X_")
    out = to_scoped_dotenv(result)
    assert 'X_MSG="hello world"' in out


def test_empty_env_returns_empty_result():
    env = EnvFile.parse("")
    result = scope_env(env, "Z_")
    assert result.scoped == {}
    assert result.clean
