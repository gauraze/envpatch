import pytest
from envpatch.parser import EnvFile
from envpatch.normalize import normalize_env, NormalizeResult


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_uppercase_key():
    env = make_env("db_host=localhost\n")
    result = normalize_env(env, uppercase_keys=True, strip_quotes=False, strip_whitespace=False)
    assert any(e.key == "DB_HOST" for e in result.entries if not e.comment)
    assert not result.clean
    assert "key uppercased" in result.issues[0].reason


def test_already_uppercase_no_issue():
    env = make_env("DB_HOST=localhost\n")
    result = normalize_env(env, uppercase_keys=True, strip_quotes=False, strip_whitespace=False)
    assert result.clean


def test_strip_double_quotes():
    env = make_env('API_KEY="secret"\n')
    result = normalize_env(env, uppercase_keys=False, strip_quotes=True, strip_whitespace=False)
    entry = next(e for e in result.entries if not e.comment)
    assert entry.value == "secret"
    assert not result.clean


def test_strip_single_quotes():
    env = make_env("TOKEN='abc'\n")
    result = normalize_env(env, uppercase_keys=False, strip_quotes=True, strip_whitespace=False)
    entry = next(e for e in result.entries if not e.comment)
    assert entry.value == "abc"


def test_strip_whitespace_in_value():
    env = make_env("HOST=  localhost  \n")
    result = normalize_env(env, uppercase_keys=False, strip_quotes=False, strip_whitespace=True)
    entry = next(e for e in result.entries if not e.comment)
    assert entry.value == "localhost"


def test_no_change_when_all_disabled():
    env = make_env('db_host=" val "\n')
    result = normalize_env(env, uppercase_keys=False, strip_quotes=False, strip_whitespace=False)
    assert result.clean


def test_keys_filter_limits_normalization():
    env = make_env("db_host=localhost\ndb_port=5432\n")
    result = normalize_env(env, uppercase_keys=True, strip_quotes=False, strip_whitespace=False, keys=["db_host"])
    keys = [e.key for e in result.entries if not e.comment]
    assert "DB_HOST" in keys
    assert "db_port" in keys


def test_to_dotenv_roundtrip():
    env = make_env("db_host=localhost\nPORT=5432\n")
    result = normalize_env(env)
    dotenv = result.to_dotenv()
    assert "DB_HOST=localhost" in dotenv
    assert "PORT=5432" in dotenv
