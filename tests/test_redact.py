"""Tests for envpatch.redact."""
import pytest

from envpatch.parser import EnvFile
from envpatch.redact import DEFAULT_PLACEHOLDER, redact


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_non_sensitive_key_unchanged():
    env = make_env("APP_NAME=myapp\nDEBUG=true\n")
    result = redact(env)
    assert result.redacted["APP_NAME"] == "myapp"
    assert result.redacted["DEBUG"] == "true"
    assert result.redacted_keys == []


def test_secret_key_redacted():
    env = make_env("DB_SECRET=supersecret\n")
    result = redact(env)
    assert result.redacted["DB_SECRET"] == DEFAULT_PLACEHOLDER
    assert "DB_SECRET" in result.redacted_keys


def test_password_key_redacted():
    env = make_env("DB_PASSWORD=hunter2\n")
    result = redact(env)
    assert result.redacted["DB_PASSWORD"] == DEFAULT_PLACEHOLDER


def test_token_key_redacted():
    env = make_env("GITHUB_TOKEN=abc123\n")
    result = redact(env)
    assert result.redacted["GITHUB_TOKEN"] == DEFAULT_PLACEHOLDER


def test_api_key_redacted():
    env = make_env("STRIPE_API_KEY=sk_live_xxx\n")
    result = redact(env)
    assert result.redacted["STRIPE_API_KEY"] == DEFAULT_PLACEHOLDER


def test_custom_placeholder():
    env = make_env("DB_PASSWORD=secret\n")
    result = redact(env, placeholder="<hidden>")
    assert result.redacted["DB_PASSWORD"] == "<hidden>"


def test_custom_patterns():
    env = make_env("INTERNAL_CODE=1234\nPUBLIC_NAME=foo\n")
    result = redact(env, patterns=[r".*CODE.*"])
    assert result.redacted["INTERNAL_CODE"] == DEFAULT_PLACEHOLDER
    assert result.redacted["PUBLIC_NAME"] == "foo"


def test_to_dotenv_output():
    env = make_env("APP=test\nDB_PASSWORD=secret\n")
    result = redact(env)
    output = result.to_dotenv()
    assert "APP=test" in output
    assert f"DB_PASSWORD={DEFAULT_PLACEHOLDER}" in output


def test_mixed_env():
    env = make_env("HOST=localhost\nAPI_KEY=key123\nPORT=5432\nSECRET_KEY=xyz\n")
    result = redact(env)
    assert result.redacted["HOST"] == "localhost"
    assert result.redacted["PORT"] == "5432"
    assert result.redacted["API_KEY"] == DEFAULT_PLACEHOLDER
    assert result.redacted["SECRET_KEY"] == DEFAULT_PLACEHOLDER
    assert len(result.redacted_keys) == 2
