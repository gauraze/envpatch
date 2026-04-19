import pytest
from click.testing import CliRunner
from pathlib import Path
from envpatch.cli_transform import transform_cmd


@pytest.fixture
def runner():
    return CliRunner()


def write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / ".env"
    p.write_text(content)
    return p


def test_transform_upper_writes_file(runner, tmp_path):
    p = write(tmp_path, "FOO=hello\nBAR=world\n")
    result = runner.invoke(transform_cmd, ["run", str(p), "--upper", "FOO"])
    assert result.exit_code == 0
    assert "FOO=HELLO" in p.read_text()
    assert "BAR=world" in p.read_text()


def test_transform_dry_run_does_not_write(runner, tmp_path):
    p = write(tmp_path, "FOO=hello\n")
    original = p.read_text()
    result = runner.invoke(transform_cmd, ["run", str(p), "--upper", "FOO", "--dry-run"])
    assert result.exit_code == 0
    assert p.read_text() == original
    assert "FOO=HELLO" in result.output


def test_transform_missing_file(runner, tmp_path):
    result = runner.invoke(transform_cmd, ["run", str(tmp_path / "missing.env"), "--upper", "FOO"])
    assert result.exit_code != 0
    assert "not found" in result.output.lower()


def test_transform_no_transforms_errors(runner, tmp_path):
    p = write(tmp_path, "FOO=hello\n")
    result = runner.invoke(transform_cmd, ["run", str(p)])
    assert result.exit_code != 0


def test_transform_lower_key(runner, tmp_path):
    p = write(tmp_path, "FOO=HELLO\n")
    result = runner.invoke(transform_cmd, ["run", str(p), "--lower", "FOO"])
    assert result.exit_code == 0
    assert "FOO=hello" in p.read_text()
