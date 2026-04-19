import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.split import split_by_prefix, to_split_dotenv


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_roundtrip_split_and_reparse(env_dir):
    raw = "DB_HOST=localhost\nDB_PORT=5432\nAPP_DEBUG=true\n"
    env = EnvFile.parse(raw)
    result = split_by_prefix(env, ["DB", "APP"])

    for grp, entries in result.groups.items():
        out = env_dir / f".env.{grp.lower()}"
        out.write_text(to_split_dotenv(entries))

    db_env = EnvFile.parse((env_dir / ".env.db").read_text())
    assert db_env.get("DB_HOST") == "localhost"
    assert db_env.get("DB_PORT") == "5432"


def test_split_preserves_all_keys(env_dir):
    raw = "DB_HOST=localhost\nAPP_NAME=myapp\nSECRET=xyz\n"
    env = EnvFile.parse(raw)
    result = split_by_prefix(env, ["DB", "APP"])

    all_keys = [
        e.key for entries in result.groups.values() for e in entries
    ] + [e.key for e in result.ungrouped]

    assert set(all_keys) == {"DB_HOST", "APP_NAME", "SECRET"}


def test_split_no_data_loss_on_strip(env_dir):
    raw = "DB_HOST=localhost\nDB_PORT=5432\n"
    env = EnvFile.parse(raw)
    result = split_by_prefix(env, ["DB"], keep_prefix=False)
    out = to_split_dotenv(result.groups["DB"])
    reparsed = EnvFile.parse(out)
    assert reparsed.get("HOST") == "localhost"
    assert reparsed.get("PORT") == "5432"
