import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.mask import mask_env


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_mask_then_reparse_valid(env_dir):
    src = "API_SECRET=topsecret\nHOST=localhost\nDB_PASSWORD=pass\n"
    env = EnvFile.parse(src)
    result = mask_env(env)
    out_text = result.to_dotenv()
    reparsed = EnvFile.parse(out_text)
    vals = {e.key: e.value for e in reparsed.entries if e.key}
    assert vals["API_SECRET"] == "***"
    assert vals["HOST"] == "localhost"
    assert vals["DB_PASSWORD"] == "***"


def test_mask_write_and_reload(env_dir):
    src = "TOKEN=abc123\nNAME=app\n"
    env = EnvFile.parse(src)
    result = mask_env(env)
    out = env_dir / "masked.env"
    out.write_text(result.to_dotenv())
    reloaded = EnvFile.parse(out.read_text())
    vals = {e.key: e.value for e in reloaded.entries if e.key}
    assert vals["TOKEN"] == "***"
    assert vals["NAME"] == "app"


def test_mask_all_sensitive_keys(env_dir):
    src = "\n".join([
        "DB_SECRET=s1", "API_TOKEN=t1", "AUTH_KEY=k1",
        "PRIVATE_DATA=p1", "APP_ENV=production"
    ]) + "\n"
    env = EnvFile.parse(src)
    result = mask_env(env)
    assert len(result.masked_keys) == 4
    vals = {e.key: e.value for e in result.entries if e.key}
    assert vals["APP_ENV"] == "production"
