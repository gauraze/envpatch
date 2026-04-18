"""Tests for envpatch.cli_audit commands."""
import json
from click.testing import CliRunner
from envpatch.cli_audit import audit_cmd
from envpatch.audit import AuditLog, save_audit


def write_log(path, entries_data):
    with open(path, "w") as fh:
        json.dump({"version": 1, "entries": entries_data}, fh)


def test_audit_list_empty(tmp_path):
    runner = CliRunner()
    log = str(tmp_path / "audit.json")
    result = runner.invoke(audit_cmd, ["list", "--log", log])
    assert result.exit_code == 0
    assert "No audit entries" in result.output


def test_audit_list_shows_entries(tmp_path):
    log_path = str(tmp_path / "audit.json")
    al = AuditLog()
    al.add(action="patch", target=".env", keys_changed=["FOO", "BAR"], source=".env.base")
    save_audit(al, log_path)
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["list", "--log", log_path])
    assert result.exit_code == 0
    assert "patch" in result.output
    assert "FOO" in result.output


def test_audit_list_filter_action(tmp_path):
    log_path = str(tmp_path / "audit.json")
    al = AuditLog()
    al.add(action="patch", target=".env", keys_changed=["A"])
    al.add(action="snapshot", target=".env", keys_changed=["B"])
    save_audit(al, log_path)
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["list", "--log", log_path, "--action", "snapshot"])
    assert result.exit_code == 0
    assert "snapshot" in result.output
    assert "patch" not in result.output


def test_audit_clear(tmp_path):
    log_path = str(tmp_path / "audit.json")
    al = AuditLog()
    al.add(action="patch", target=".env", keys_changed=["X"])
    save_audit(al, log_path)
    runner = CliRunner()
    result = runner.invoke(audit_cmd, ["clear", "--log", log_path], input="y\n")
    assert result.exit_code == 0
    assert "cleared" in result.output
    with open(log_path) as fh:
        data = json.load(fh)
    assert data["entries"] == []
