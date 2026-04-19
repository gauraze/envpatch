import pytest
from envpatch.parser import EnvFile
from envpatch.trim import trim_env, to_trimmed_dotenv


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_trim_by_exact_key():
    env = make_env("FOO=1\nBAR=2\nBAZ=3")
    result = trim_env(env, keys=["BAR"])
    keys = [e.key for e in result.entries]
    assert "BAR" not in keys
    assert "FOO" in keys
    assert "BAZ" in keys
    assert result.removed == ["BAR"]


def test_trim_by_prefix():
    env = make_env("DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=test")
    result = trim_env(env, prefixes=["DB_"])
    keys = [e.key for e in result.entries]
    assert "DB_HOST" not in keys
    assert "DB_PORT" not in keys
    assert "APP_NAME" in keys
    assert len(result.removed) == 2


def test_trim_empty_only_skips_nonempty():
    env = make_env("FOO=\nBAR=hello")
    result = trim_env(env, keys=["FOO", "BAR"], empty_only=True)
    keys = [e.key for e in result.entries]
    assert "FOO" not in keys
    assert "BAR" in keys
    assert result.removed == ["FOO"]


def test_trim_no_match_returns_clean():
    env = make_env("FOO=1\nBAR=2")
    result = trim_env(env, keys=["MISSING"])
    assert result.clean
    assert len(result.entries) == 2


def test_to_trimmed_dotenv_output():
    env = make_env("FOO=1\nBAR=2\nBAZ=3")
    result = trim_env(env, keys=["BAR"])
    out = to_trimmed_dotenv(result)
    assert "BAR" not in out
    assert "FOO=1" in out
    assert "BAZ=3" in out


def test_trim_multiple_keys():
    env = make_env("A=1\nB=2\nC=3\nD=4")
    result = trim_env(env, keys=["A", "C"])
    keys = [e.key for e in result.entries]
    assert keys == ["B", "D"]
    assert set(result.removed) == {"A", "C"}
