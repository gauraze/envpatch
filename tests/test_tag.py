import pytest
from envpatch.parser import EnvFile
from envpatch.tag import tag_env, to_tagged_dotenv


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_tag_single_key():
    env = make_env("API_KEY=secret\nDEBUG=true\n")
    result = tag_env(env, {"API_KEY": "sensitive"})
    assert "API_KEY" in result.tagged
    assert result.tagged["API_KEY"] == ["sensitive"]


def test_tag_skips_missing_key():
    env = make_env("API_KEY=secret\n")
    result = tag_env(env, {"MISSING": "label"})
    assert "MISSING" in result.skipped
    assert result.clean is False


def test_tag_skips_key_not_in_tag_map():
    env = make_env("API_KEY=secret\nDEBUG=true\n")
    result = tag_env(env, {"API_KEY": "sensitive"}, keys=["API_KEY", "DEBUG"])
    assert "DEBUG" in result.skipped


def test_tag_clean_when_all_tagged():
    env = make_env("API_KEY=secret\n")
    result = tag_env(env, {"API_KEY": "sensitive"}, keys=["API_KEY"])
    assert result.clean is True


def test_to_tagged_dotenv_appends_comment():
    env = make_env("API_KEY=secret\nDEBUG=true\n")
    result = tag_env(env, {"API_KEY": "sensitive"})
    output = to_tagged_dotenv(env, result)
    assert "# [sensitive]" in output
    assert "DEBUG=true" in output


def test_to_tagged_dotenv_untagged_keys_unchanged():
    env = make_env("HOST=localhost\nPORT=5432\n")
    result = tag_env(env, {"HOST": "infra"})
    output = to_tagged_dotenv(env, result)
    assert "PORT=5432" in output
    assert "# [infra]" in output


def test_tag_multiple_keys():
    env = make_env("A=1\nB=2\nC=3\n")
    result = tag_env(env, {"A": "alpha", "B": "beta"})
    assert "A" in result.tagged
    assert "B" in result.tagged
    assert result.tagged["A"] == ["alpha"]
    assert result.tagged["B"] == ["beta"]
