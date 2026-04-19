import pytest
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.transform import apply_transforms, to_transformed_dotenv


@pytest.fixture
def env_dir(tmp_path):
    return tmp_path


def test_roundtrip_upper_and_reparse(env_dir):
    p = env_dir / ".env"
    p.write_text("FOO=hello\nBAR=world\n")
    env = EnvFile.parse(p.read_text())
    result = apply_transforms(env, {"*": str.upper})
    output = to_transformed_dotenv(result)
    p.write_text(output)
    reparsed = EnvFile.parse(p.read_text())
    assert reparsed.get("FOO") == "HELLO"
    assert reparsed.get("BAR") == "WORLD"


def test_chained_transforms_preserve_all_keys(env_dir):
    p = env_dir / ".env"
    p.write_text("FOO=hello\nBAR=  spaced  \nBAZ=MiXeD\n")
    env = EnvFile.parse(p.read_text())
    r1 = apply_transforms(env, {"BAR": str.strip})
    env2 = EnvFile(entries=r1.entries)
    r2 = apply_transforms(env2, {"BAZ": str.lower})
    values = {e.key: e.value for e in r2.entries if e.key}
    assert values["FOO"] == "hello"
    assert values["BAR"] == "spaced"
    assert values["BAZ"] == "mixed"


def test_transform_does_not_drop_comments(env_dir):
    p = env_dir / ".env"
    p.write_text("# my comment\nFOO=hello\n")
    env = EnvFile.parse(p.read_text())
    result = apply_transforms(env, {"FOO": str.upper})
    output = to_transformed_dotenv(result)
    assert "# my comment" in output
    assert "FOO=HELLO" in output
