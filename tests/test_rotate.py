import pytest
from envpatch.parser import EnvFile
from envpatch.rotate import rotate_keys, apply_rotation, to_rotated_dotenv


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_rotate_single_key():
    env = make_env("DB_PASS=old\nAPI_KEY=abc\n")
    result = rotate_keys(env, {"DB_PASS": "new_secret"})
    assert result.rotated == {"DB_PASS": "new_secret"}
    assert result.skipped == []


def test_rotate_missing_key_skipped():
    env = make_env("FOO=bar\n")
    result = rotate_keys(env, {"MISSING": "value"})
    assert result.rotated == {}
    assert "MISSING" in result.skipped


def test_rotate_key_not_in_replacements_skipped():
    env = make_env("FOO=bar\nBAZ=qux\n")
    result = rotate_keys(env, {"FOO": "new"}, keys=["FOO", "BAZ"])
    assert "BAZ" in result.skipped
    assert result.rotated == {"FOO": "new"}


def test_rotate_clean_when_nothing_rotated():
    env = make_env("FOO=bar\n")
    result = rotate_keys(env, {"MISSING": "x"})
    assert result.clean


def test_apply_rotation_updates_values():
    env = make_env("SECRET=old\nOTHER=keep\n")
    result = rotate_keys(env, {"SECRET": "new_val"})
    updated = apply_rotation(env, result)
    assert updated.get("SECRET") == "new_val"
    assert updated.get("OTHER") == "keep"


def test_to_rotated_dotenv_output():
    env = make_env("TOKEN=abc123\nFOO=bar\n")
    result = rotate_keys(env, {"TOKEN": "xyz789"})
    out = to_rotated_dotenv(env, result)
    assert "TOKEN=xyz789" in out
    assert "FOO=bar" in out


def test_rotate_multiple_keys():
    env = make_env("A=1\nB=2\nC=3\n")
    result = rotate_keys(env, {"A": "10", "B": "20"})
    assert result.rotated == {"A": "10", "B": "20"}
    updated = apply_rotation(env, result)
    assert updated.get("A") == "10"
    assert updated.get("B") == "20"
    assert updated.get("C") == "3"
