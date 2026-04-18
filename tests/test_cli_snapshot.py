"""Integration tests for snapshot CLI commands."""
import json
from click.testing import CliRunner
from envpatch.cli_snapshot import snapshot_cmd


ENV_CONTENT = "FOO=bar\nBAZ=qux\n"
ENV_CONTENT_MODIFIED = "FOO=changed\nBAZ=qux\nNEW=val\n"


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_snapshot_save(tmp_path):
    env_file = write(tmp_path, ".env", ENV_CONTENT)
    snap_file = str(tmp_path / "snap.json")
    runner = CliRunner()
    result = runner.invoke(snapshot_cmd, ["save", env_file, snap_file])
    assert result.exit_code == 0
    assert "Snapshot saved" in result.output
    data = json.loads(open(snap_file).read())
    assert len(data["entries"]) == 2


def test_snapshot_info(tmp_path):
    env_file = write(tmp_path, ".env", ENV_CONTENT)
    snap_file = str(tmp_path / "snap.json")
    runner = CliRunner()
    runner.invoke(snapshot_cmd, ["save", env_file, snap_file, "--label", "ci"])
    result = runner.invoke(snapshot_cmd, ["info", snap_file])
    assert result.exit_code == 0
    assert "ci" in result.output
    assert "Keys      : 2" in result.output


def test_snapshot_diff_changes(tmp_path):
    env_file = write(tmp_path, ".env", ENV_CONTENT)
    snap_file = str(tmp_path / "snap.json")
    env_file2 = write(tmp_path, ".env2", ENV_CONTENT_MODIFIED)
    runner = CliRunner()
    runner.invoke(snapshot_cmd, ["save", env_file, snap_file])
    result = runner.invoke(snapshot_cmd, ["diff", snap_file, env_file2])
    assert result.exit_code == 0
    assert "FOO" in result.output


def test_snapshot_diff_no_changes(tmp_path):
    env_file = write(tmp_path, ".env", ENV_CONTENT)
    snap_file = str(tmp_path / "snap.json")
    runner = CliRunner()
    runner.invoke(snapshot_cmd, ["save", env_file, snap_file])
    result = runner.invoke(snapshot_cmd, ["diff", snap_file, env_file])
    assert result.exit_code == 0
    assert "No differences" in result.output
