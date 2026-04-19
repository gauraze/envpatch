import json
import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.freeze import freeze_env, check_freeze


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def write_env(path, content):
    p = path / ".env"
    p.write_text(content)
    return p


def test_freeze_roundtrip_no_drift(env_dir):
    p = write_env(env_dir, "DB_HOST=localhost\nDB_PORT=5432\n")
    env = EnvFile.parse(p.read_text())
    frozen = freeze_env(env)
    result = check_freeze(env, frozen)
    assert result.clean


def test_freeze_detects_value_change(env_dir):
    p = write_env(env_dir, "DB_HOST=localhost\n")
    env = EnvFile.parse(p.read_text())
    frozen = freeze_env(env)
    # simulate drift
    p.write_text("DB_HOST=remotehost\n")
    env2 = EnvFile.parse(p.read_text())
    result = check_freeze(env2, frozen)
    assert not result.clean
    assert result.violations[0].key == "DB_HOST"


def test_freeze_lock_file_persisted(env_dir):
    p = write_env(env_dir, "SECRET=abc123\n")
    env = EnvFile.parse(p.read_text())
    frozen = freeze_env(env)
    lock = env_dir / "freeze.lock.json"
    lock.write_text(json.dumps(frozen))
    loaded = json.loads(lock.read_text())
    assert loaded["SECRET"] == "abc123"


def test_freeze_subset_ignores_extra_keys(env_dir):
    p = write_env(env_dir, "A=1\nB=2\nC=3\n")
    env = EnvFile.parse(p.read_text())
    frozen = freeze_env(env, keys=["A"])
    # change B — should not affect check
    p.write_text("A=1\nB=changed\nC=3\n")
    env2 = EnvFile.parse(p.read_text())
    result = check_freeze(env2, frozen)
    assert result.clean
