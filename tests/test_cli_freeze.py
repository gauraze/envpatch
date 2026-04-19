import json
import pytest
from click.testing import CliRunner
from envpatch.cli_freeze import freeze_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_freeze_lock_creates_file(runner, tmp_path):
    env_file = write(tmp_path, ".env", "A=1\nB=2\n")
    lock_file = str(tmp_path / "freeze.lock.json")
    result = runner.invoke(freeze_cmd, ["lock", env_file, lock_file])
    assert result.exit_code == 0
    data = json.loads(open(lock_file).read())
    assert data == {"A": "1", "B": "2"}


def test_freeze_lock_subset(runner, tmp_path):
    env_file = write(tmp_path, ".env", "A=1\nB=2\nC=3\n")
    lock_file = str(tmp_path / "freeze.lock.json")
    result = runner.invoke(freeze_cmd, ["lock", env_file, lock_file, "-k", "A", "-k", "C"])
    assert result.exit_code == 0
    data = json.loads(open(lock_file).read())
    assert "B" not in data
    assert data["A"] == "1"


def test_freeze_check_passes(runner, tmp_path):
    env_file = write(tmp_path, ".env", "A=1\nB=2\n")
    lock_file = write(tmp_path, "freeze.lock.json", json.dumps({"A": "1", "B": "2"}))
    result = runner.invoke(freeze_cmd, ["check", env_file, lock_file])
    assert result.exit_code == 0
    assert "OK" in result.output


def test_freeze_check_fails_on_drift(runner, tmp_path):
    env_file = write(tmp_path, ".env", "A=changed\nB=2\n")
    lock_file = write(tmp_path, "freeze.lock.json", json.dumps({"A": "original", "B": "2"}))
    result = runner.invoke(freeze_cmd, ["check", env_file, lock_file])
    assert result.exit_code == 1
    assert "DRIFT" in result.output


def test_freeze_check_fails_on_missing_key(runner, tmp_path):
    env_file = write(tmp_path, ".env", "B=2\n")
    lock_file = write(tmp_path, "freeze.lock.json", json.dumps({"A": "1", "B": "2"}))
    result = runner.invoke(freeze_cmd, ["check", env_file, lock_file])
    assert result.exit_code == 1
