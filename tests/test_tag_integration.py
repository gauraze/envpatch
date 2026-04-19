import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.tag import tag_env, to_tagged_dotenv


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_tag_roundtrip_parseable(env_dir):
    content = "API_KEY=secret\nDEBUG=false\n"
    env = EnvFile.parse(content)
    result = tag_env(env, {"API_KEY": "sensitive"})
    output = to_tagged_dotenv(env, result)
    reparsed = EnvFile.parse(output)
    assert reparsed.get("API_KEY") is not None
    assert reparsed.get("DEBUG") == "false"


def test_tag_does_not_drop_keys(env_dir):
    content = "A=1\nB=2\nC=3\n"
    env = EnvFile.parse(content)
    result = tag_env(env, {"A": "first", "C": "third"})
    output = to_tagged_dotenv(env, result)
    reparsed = EnvFile.parse(output)
    assert set(reparsed.keys()) == {"A", "B", "C"}


def test_tag_write_and_reload(env_dir):
    env_path = env_dir / ".env"
    env_path.write_text("SECRET=xyz\nHOST=localhost\n")
    env = EnvFile.parse(env_path.read_text())
    result = tag_env(env, {"SECRET": "confidential"})
    env_path.write_text(to_tagged_dotenv(env, result))
    reloaded = EnvFile.parse(env_path.read_text())
    assert reloaded.get("HOST") == "localhost"
