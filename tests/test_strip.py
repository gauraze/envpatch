import pytest
from envpatch.parser import EnvFile
from envpatch.strip import strip_keys, to_stripped_dotenv


def make_env(pairs: dict) -> EnvFile:
    text = "\n".join(f"{k}={v}" for k, v in pairs.items())
    return EnvFile.parse(text)


def test_strip_exact_key():
    env = make_env({"FOO": "1", "BAR": "2", "BAZ": "3"})
    new_env, result = strip_keys(env, ["BAR"])
    assert "BAR" in result.removed
    assert "FOO" in result.kept
    assert "BAZ" in result.kept
    assert new_env.get("BAR") is None


def test_strip_by_prefix():
    env = make_env({"TEST_A": "1", "TEST_B": "2", "PROD_C": "3"})
    new_env, result = strip_keys(env, [], prefix="TEST_")
    assert "TEST_A" in result.removed
    assert "TEST_B" in result.removed
    assert "PROD_C" in result.kept


def test_strip_by_suffix():
    env = make_env({"DB_SECRET": "x", "API_SECRET": "y", "HOST": "z"})
    new_env, result = strip_keys(env, [], suffix="_SECRET")
    assert "DB_SECRET" in result.removed
    assert "API_SECRET" in result.removed
    assert "HOST" in result.kept


def test_strip_no_match_returns_clean():
    env = make_env({"FOO": "1", "BAR": "2"})
    new_env, result = strip_keys(env, ["MISSING"])
    assert result.clean
    assert len(result.kept) == 2


def test_strip_combined_exact_and_prefix():
    env = make_env({"ALPHA": "1", "BETA_X": "2", "GAMMA": "3"})
    new_env, result = strip_keys(env, ["GAMMA"], prefix="BETA_")
    assert "BETA_X" in result.removed
    assert "GAMMA" in result.removed
    assert "ALPHA" in result.kept


def test_to_stripped_dotenv_format():
    env = make_env({"KEY": "value", "OTHER": "data"})
    new_env, _ = strip_keys(env, ["OTHER"])
    output = to_stripped_dotenv(new_env)
    assert "KEY=value" in output
    assert "OTHER" not in output
