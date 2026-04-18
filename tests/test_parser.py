"""Tests for envpatch.parser."""
from pathlib import Path

import pytest

from envpatch.parser import parse_env_file, EnvEntry


@pytest.fixture()
def simple_env(tmp_path: Path) -> Path:
    content = (
        "# Database config\n"
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "\n"
        "SECRET_KEY=\"my secret\"\n"
        "EMPTY_VAR=\n"
    )
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_parse_keys(simple_env):
    env = parse_env_file(simple_env)
    assert set(env.keys()) == {"DB_HOST", "DB_PORT", "SECRET_KEY", "EMPTY_VAR"}


def test_parse_values(simple_env):
    env = parse_env_file(simple_env)
    assert env.get("DB_HOST").value == "localhost"
    assert env.get("DB_PORT").value == "5432"


def test_strip_quotes(simple_env):
    env = parse_env_file(simple_env)
    assert env.get("SECRET_KEY").value == "my secret"


def test_empty_value(simple_env):
    env = parse_env_file(simple_env)
    assert env.get("EMPTY_VAR").value == ""


def test_comment_attached(simple_env):
    env = parse_env_file(simple_env)
    assert env.get("DB_HOST").comment == "Database config"


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "missing.env")
