import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.dedupe import dedupe_env, to_deduped_dotenv


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_roundtrip_no_data_loss(env_dir):
    content = "# header\nA=1\nB=2\nC=3\n"
    path = env_dir / ".env"
    path.write_text(content)
    env = EnvFile.parse(path.read_text())
    result = dedupe_env(env)
    assert result.clean
    assert len(result.cleaned) == len(env.entries)


def test_dedupe_multiple_keys(env_dir):
    content = "A=1\nB=x\nA=2\nC=3\nB=y\n"
    path = env_dir / ".env"
    path.write_text(content)
    env = EnvFile.parse(path.read_text())
    result = dedupe_env(env, keep="last")
    assert "A" in result.duplicates
    assert "B" in result.duplicates
    keys = [e.key for e in result.cleaned if e.key]
    assert keys.count("A") == 1
    assert keys.count("B") == 1


def test_write_and_reparse_is_clean(env_dir):
    content = "A=1\nA=2\nB=3\n"
    path = env_dir / ".env"
    path.write_text(content)
    env = EnvFile.parse(path.read_text())
    result = dedupe_env(env, keep="first")
    output = to_deduped_dotenv(result)
    path.write_text(output)
    env2 = EnvFile.parse(path.read_text())
    result2 = dedupe_env(env2)
    assert result2.clean
