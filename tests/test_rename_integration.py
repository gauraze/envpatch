"""Integration tests: rename through full parse -> rename -> serialize cycle."""
from pathlib import Path
import pytest
from envpatch.parser import EnvFile
from envpatch.rename import rename_keys


@pytest.fixture
def env_dir(tmp_path):
    (tmp_path / "app.env").write_text(
        "DB_HOST=localhost\nDB_PORT=5432\nSECRET_KEY=abc123\n"
    )
    return tmp_path


def test_rename_and_serialize_roundtrip(env_dir):
    src = env_dir / "app.env"
    env = EnvFile.parse(src.read_text())
    result = rename_keys(env, {"DB_HOST": "DATABASE_HOST"})
    assert result.output.get("DATABASE_HOST") == "localhost"
    assert result.output.get("DB_HOST") is None
    dotenv = result.output.to_dotenv()
    assert "DATABASE_HOST=localhost" in dotenv


def test_rename_does_not_lose_keys(env_dir):
    src = env_dir / "app.env"
    env = EnvFile.parse(src.read_text())
    result = rename_keys(env, {"DB_PORT": "DATABASE_PORT"})
    keys = result.output.keys()
    assert "DB_HOST" in keys
    assert "DATABASE_PORT" in keys
    assert "SECRET_KEY" in keys
    assert len(keys) == 3


def test_rename_multiple_in_one_pass(env_dir):
    src = env_dir / "app.env"
    env = EnvFile.parse(src.read_text())
    result = rename_keys(env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert result.output.get("DATABASE_HOST") == "localhost"
    assert result.output.get("DATABASE_PORT") == "5432"
    assert len(result.renamed) == 2
