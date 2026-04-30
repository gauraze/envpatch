"""CLI tests for envpatch.cli_pivot."""
import pytest
from click.testing import CliRunner

from envpatch.cli_pivot import pivot_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


def test_pivot_show_basic(runner, tmp_path):
    dev = write(tmp_path, "dev.env", "A=1\nB=2\n")
    prod = write(tmp_path, "prod.env", "A=10\nB=20\n")
    result = runner.invoke(pivot_cmd, ["show", dev, prod, "--labels", "dev,prod"])
    assert result.exit_code == 0
    assert "KEY" in result.output
    assert "dev" in result.output
    assert "prod" in result.output
    assert "A" in result.output


def test_pivot_show_missing_key_warns(runner, tmp_path):
    dev = write(tmp_path, "dev.env", "A=1\nB=2\n")
    prod = write(tmp_path, "prod.env", "A=10\n")
    result = runner.invoke(pivot_cmd, ["show", dev, prod])
    assert result.exit_code == 0
    assert "<missing>" in result.output


def test_pivot_show_custom_missing_marker(runner, tmp_path):
    dev = write(tmp_path, "dev.env", "A=1\nB=2\n")
    prod = write(tmp_path, "prod.env", "A=10\n")
    result = runner.invoke(
        pivot_cmd, ["show", dev, prod, "--missing", "N/A"]
    )
    assert "N/A" in result.output


def test_pivot_show_label_mismatch_error(runner, tmp_path):
    dev = write(tmp_path, "dev.env", "A=1\n")
    prod = write(tmp_path, "prod.env", "A=10\n")
    result = runner.invoke(
        pivot_cmd, ["show", dev, prod, "--labels", "dev,staging,prod"]
    )
    assert result.exit_code != 0
    assert "labels length" in result.output


def test_pivot_show_no_header(runner, tmp_path):
    dev = write(tmp_path, "dev.env", "A=1\n")
    result = runner.invoke(pivot_cmd, ["show", dev, "--no-header"])
    assert result.exit_code == 0
    assert "KEY" not in result.output
    assert "A" in result.output
