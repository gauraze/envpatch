"""Tests for envpatch.cli_watch."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from envpatch.cli_watch import watch_cmd
from envpatch.watch import WatchEvent
from envpatch.diff import DiffEntry, ChangeType


def test_watch_start_missing_file(tmp_path):
    runner = CliRunner()
    result = runner.invoke(watch_cmd, ["start", str(tmp_path / "missing.env")])
    assert result.exit_code != 0


def test_watch_start_calls_watch(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\n")

    runner = CliRunner()
    with patch("envpatch.cli_watch.watch_env_file") as mock_watch:
        result = runner.invoke(watch_cmd, ["start", str(env_file), "--interval", "0.5"])
    assert result.exit_code == 0
    mock_watch.assert_called_once()
    _, kwargs = mock_watch.call_args
    assert kwargs.get("interval") == 0.5 or mock_watch.call_args[0][2] == 0.5


def test_print_event_output(tmp_path, capsys):
    from envpatch.cli_watch import _print_event
    entry = DiffEntry(key="BAR", change_type=ChangeType.ADDED, new_value="baz")
    event = WatchEvent(path=Path(".env"), changes=[entry])
    _print_event(event)
    captured = capsys.readouterr()
    assert "BAR" in captured.out
    assert ".env" in captured.out
