"""Integration tests for defaults: parse -> apply -> serialize -> reparse."""
from __future__ import annotations
import pytest
from envpatch.parser import EnvFile
from envpatch.defaults import apply_defaults, to_defaults_dotenv


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_roundtrip_preserves_all_keys(env_dir):
    src = "A=1\nB=2\n"
    env = EnvFile.parse(src)
    result = apply_defaults(env, {"C": "3"})
    output = to_defaults_dotenv(result)
    reparsed = EnvFile.parse(output)
    keys = reparsed.keys()
    assert "A" in keys
    assert "B" in keys
    assert "C" in keys


def test_overwrite_then_reparse(env_dir):
    src = "HOST=localhost\nPORT=5432\n"
    env = EnvFile.parse(src)
    result = apply_defaults(env, {"HOST": "remotehost"}, overwrite=True)
    output = to_defaults_dotenv(result)
    reparsed = EnvFile.parse(output)
    assert reparsed.get("HOST") == "remotehost"
    assert reparsed.get("PORT") == "5432"


def test_apply_to_empty_file(env_dir):
    env = EnvFile.parse("")
    result = apply_defaults(env, {"DEBUG": "true", "LOG_LEVEL": "info"})
    output = to_defaults_dotenv(result)
    reparsed = EnvFile.parse(output)
    assert reparsed.get("DEBUG") == "true"
    assert reparsed.get("LOG_LEVEL") == "info"


def test_no_defaults_output_unchanged(env_dir):
    src = "FOO=bar\n"
    env = EnvFile.parse(src)
    result = apply_defaults(env, {})
    output = to_defaults_dotenv(result)
    reparsed = EnvFile.parse(output)
    assert reparsed.keys() == env.keys()
