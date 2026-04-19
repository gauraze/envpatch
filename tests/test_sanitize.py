import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.sanitize import sanitize_env, SanitizeResult


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, comment=None) for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_clean_env_no_issues():
    env = make_env({"HOST": "localhost", "PORT": "5432"})
    result = sanitize_env(env)
    assert result.clean
    assert len(result.entries) == 2


def test_strips_leading_trailing_whitespace():
    env = make_env({"HOST": "  localhost  "})
    result = sanitize_env(env, strip_whitespace=True)
    assert not result.clean
    assert result.entries[0].value == "localhost"
    assert any("whitespace" in i.reason for i in result.issues)


def test_no_strip_whitespace_when_disabled():
    env = make_env({"HOST": "  localhost  "})
    result = sanitize_env(env, strip_whitespace=False)
    assert result.entries[0].value == "  localhost  "


def test_strips_control_characters():
    env = make_env({"KEY": "val\x01ue"})
    result = sanitize_env(env, strip_control=True)
    assert result.entries[0].value == "value"
    assert any("control" in i.reason for i in result.issues)


def test_remove_empty_keys():
    env = make_env({"EMPTY": "", "FULL": "yes"})
    result = sanitize_env(env, remove_empty=True)
    keys = [e.key for e in result.entries]
    assert "EMPTY" not in keys
    assert "FULL" in keys
    assert any("empty" in i.reason for i in result.issues)


def test_keep_empty_keys_by_default():
    env = make_env({"EMPTY": ""})
    result = sanitize_env(env, remove_empty=False)
    assert len(result.entries) == 1


def test_allowed_keys_filters_others():
    env = make_env({"ALLOWED": "yes", "BLOCKED": "no"})
    result = sanitize_env(env, allowed_keys=["ALLOWED"])
    keys = [e.key for e in result.entries]
    assert "ALLOWED" in keys
    assert "BLOCKED" not in keys
    assert any("not in allowed" in i.reason for i in result.issues)


def test_to_dotenv_format():
    env = make_env({"A": "1", "B": "2"})
    result = sanitize_env(env)
    output = result.to_dotenv()
    assert "A=1" in output
    assert "B=2" in output
