"""Integration tests for the pivot feature (pivot_envs + serialisation)."""
import pytest

from envpatch.parser import EnvFile, EnvEntry
from envpatch.pivot import pivot_envs


@pytest.fixture()
def env_dir(tmp_path):
    return tmp_path


def _write(env_dir, name, content):
    p = env_dir / name
    p.write_text(content)
    return p


def test_three_files_pivot_correct_shape(env_dir):
    _write(env_dir, "dev.env", "A=1\nB=2\nC=3\n")
    _write(env_dir, "staging.env", "A=10\nB=20\n")
    _write(env_dir, "prod.env", "A=100\nB=200\nC=300\n")

    files = [
        EnvFile.parse((env_dir / n).read_text())
        for n in ("dev.env", "staging.env", "prod.env")
    ]
    result = pivot_envs(files, labels=["dev", "staging", "prod"])

    assert len(result.rows) == 3          # A, B, C
    assert result.rows["C"] == ["3", None, "300"]
    assert result.clean is False


def test_to_table_roundtrip_row_count(env_dir):
    _write(env_dir, "a.env", "X=1\nY=2\nZ=3\n")
    _write(env_dir, "b.env", "X=9\nY=8\nZ=7\n")

    files = [EnvFile.parse((env_dir / n).read_text()) for n in ("a.env", "b.env")]
    result = pivot_envs(files, labels=["a", "b"])
    table = result.to_table()

    # header + 3 data rows
    assert len(table) == 4
    assert table[0] == ["KEY", "a", "b"]


def test_all_files_complete_is_clean(env_dir):
    _write(env_dir, "a.env", "FOO=bar\nBAZ=qux\n")
    _write(env_dir, "b.env", "FOO=bar2\nBAZ=qux2\n")

    files = [EnvFile.parse((env_dir / n).read_text()) for n in ("a.env", "b.env")]
    result = pivot_envs(files)
    assert result.clean is True
