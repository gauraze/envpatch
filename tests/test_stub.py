"""Tests for envpatch.stub."""
import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.stub import stub_env, to_stub_dotenv, StubResult


def make_env(pairs: dict[str, str]) -> EnvFile:
    text = "\n".join(f"{k}={v}" for k, v in pairs.items())
    return EnvFile.parse(text)


def test_stub_new_keys_generated():
    result = stub_env(["DB_HOST", "DB_PORT"])
    assert "DB_HOST" in result.generated
    assert "DB_PORT" in result.generated
    assert len(result.entries) == 2


def test_stub_empty_placeholder_by_default():
    result = stub_env(["API_KEY"])
    entry = result.entries[0]
    assert entry.value == ""


def test_stub_custom_placeholder():
    result = stub_env(["API_KEY"], placeholder="CHANGEME")
    assert result.entries[0].value == "CHANGEME"


def test_stub_skips_existing_without_overwrite():
    existing = make_env({"DB_HOST": "localhost"})
    result = stub_env(["DB_HOST", "DB_PORT"], existing=existing)
    assert "DB_HOST" not in result.generated
    assert "DB_PORT" in result.generated
    # existing value preserved
    db_host = next(e for e in result.entries if e.key == "DB_HOST")
    assert db_host.value == "localhost"


def test_stub_overwrites_existing_when_flag():
    existing = make_env({"DB_HOST": "localhost"})
    result = stub_env(["DB_HOST"], placeholder="REPLACE", existing=existing, overwrite=True)
    assert "DB_HOST" in result.generated
    db_host = next(e for e in result.entries if e.key == "DB_HOST")
    assert db_host.value == "REPLACE"


def test_stub_clean_when_nothing_generated():
    existing = make_env({"KEY": "val"})
    result = stub_env(["KEY"], existing=existing)
    assert result.clean


def test_to_stub_dotenv_format():
    result = stub_env(["A", "B"], placeholder="x")
    out = to_stub_dotenv(result)
    assert "A=x" in out
    assert "B=x" in out


def test_to_stub_dotenv_empty_value():
    result = stub_env(["EMPTY"])
    out = to_stub_dotenv(result)
    assert "EMPTY=" in out
