import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.rotate import rotate_keys, apply_rotation, to_rotated_dotenv


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_roundtrip_rotate_and_reparse(env_dir):
    original = "DB_PASSWORD=hunter2\nAPI_KEY=abc\nDEBUG=true\n"
    env = EnvFile.parse(original)
    result = rotate_keys(env, {"DB_PASSWORD": "sup3rs3cr3t", "API_KEY": "newkey"})
    out = to_rotated_dotenv(env, result)
    reparsed = EnvFile.parse(out)
    assert reparsed.get("DB_PASSWORD") == "sup3rs3cr3t"
    assert reparsed.get("API_KEY") == "newkey"
    assert reparsed.get("DEBUG") == "true"


def test_rotate_does_not_drop_keys(env_dir):
    text = "A=1\nB=2\nC=3\nD=4\n"
    env = EnvFile.parse(text)
    result = rotate_keys(env, {"B": "99"})
    out = to_rotated_dotenv(env, result)
    reparsed = EnvFile.parse(out)
    assert set(reparsed.keys()) == {"A", "B", "C", "D"}


def test_rotate_file_persisted(env_dir):
    p = env_dir / ".env"
    p.write_text("SECRET=old\nFOO=keep\n")
    env = EnvFile.parse(p.read_text())
    result = rotate_keys(env, {"SECRET": "fresh"})
    p.write_text(to_rotated_dotenv(env, result))
    reloaded = EnvFile.parse(p.read_text())
    assert reloaded.get("SECRET") == "fresh"
    assert reloaded.get("FOO") == "keep"
