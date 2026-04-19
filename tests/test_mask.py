import pytest
from envpatch.parser import EnvFile
from envpatch.mask import mask_env, DEFAULT_MASK


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_secret_key_masked():
    env = make_env("DB_SECRET=hunter2\nAPP_NAME=myapp\n")
    result = mask_env(env)
    vals = {e.key: e.value for e in result.entries if e.key}
    assert vals["DB_SECRET"] == DEFAULT_MASK
    assert vals["APP_NAME"] == "myapp"
    assert "DB_SECRET" in result.masked_keys


def test_password_key_masked():
    env = make_env("DB_PASSWORD=secret\n")
    result = mask_env(env)
    assert "DB_PASSWORD" in result.masked_keys


def test_non_sensitive_key_unchanged():
    env = make_env("HOST=localhost\nPORT=5432\n")
    result = mask_env(env)
    assert result.clean
    assert result.masked_keys == []


def test_explicit_keys_override_patterns():
    env = make_env("CUSTOM=value\nDB_SECRET=s\n")
    result = mask_env(env, keys=["CUSTOM"])
    vals = {e.key: e.value for e in result.entries if e.key}
    assert vals["CUSTOM"] == DEFAULT_MASK
    assert vals["DB_SECRET"] == "s"  # not matched because keys= used


def test_custom_placeholder():
    env = make_env("API_TOKEN=abc123\n")
    result = mask_env(env, placeholder="[HIDDEN]")
    vals = {e.key: e.value for e in result.entries if e.key}
    assert vals["API_TOKEN"] == "[HIDDEN]"


def test_custom_pattern():
    env = make_env("INTERNAL_CODE=xyz\nPUBLIC=ok\n")
    result = mask_env(env, patterns=["CODE"])
    assert "INTERNAL_CODE" in result.masked_keys
    assert "PUBLIC" not in result.masked_keys


def test_to_dotenv_preserves_structure():
    env = make_env("# comment\nAPI_KEY=secret\nHOST=localhost\n")
    result = mask_env(env)
    output = result.to_dotenv()
    assert "# comment" in output
    assert "HOST=localhost" in output
    assert f"API_KEY={DEFAULT_MASK}" in output
