import os
import pytest
from click.testing import CliRunner
from envpatch.cli_promote import promote_cmd


@pytest.fixture
def profiles(tmp_path):
    (tmp_path / ".env.staging").write_text("DB_HOST=staging-db\nSECRET=abc\n")
    (tmp_path / ".env.production").write_text("DB_HOST=prod-db\n")
    return tmp_path


def test_promote_dry_run(profiles):
    runner = CliRunner()
    result = runner.invoke(
        promote_cmd,
        ["run", "staging", "production", "--base-dir", str(profiles), "--dry-run"],
    )
    assert result.exit_code == 0
    assert "dry-run" in result.output
    # production file should be unchanged
    content = (profiles / ".env.production").read_text()
    assert "SECRET" not in content


def test_promote_writes_file(profiles):
    runner = CliRunner()
    result = runner.invoke(
        promote_cmd,
        ["run", "staging", "production", "--base-dir", str(profiles),
         "--keys", "SECRET"],
    )
    assert result.exit_code == 0
    content = (profiles / ".env.production").read_text()
    assert "SECRET=abc" in content


def test_promote_conflict_aborts_without_overwrite(profiles):
    runner = CliRunner()
    result = runner.invoke(
        promote_cmd,
        ["run", "staging", "production", "--base-dir", str(profiles)],
    )
    assert result.exit_code == 1
    assert "Conflicts" in result.output or "resolve" in result.output


def test_promote_conflict_overwrites_with_flag(profiles):
    runner = CliRunner()
    result = runner.invoke(
        promote_cmd,
        ["run", "staging", "production", "--base-dir", str(profiles), "--overwrite"],
    )
    assert result.exit_code == 0
    content = (profiles / ".env.production").read_text()
    assert "DB_HOST=staging-db" in content
