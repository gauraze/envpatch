import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.flatten import flatten_envs, to_flattened_dotenv


def make_env(pairs: dict) -> EnvFile:
    entries = [
        EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}")
        for k, v in pairs.items()
    ]
    return EnvFile(entries=entries)


def test_flatten_single_file():
    env = make_env({"A": "1", "B": "2"})
    result = flatten_envs([env], labels=["base"])
    assert result.clean
    keys = [e.key for e in result.entries]
    assert keys == ["A", "B"]


def test_flatten_two_files_no_conflict():
    base = make_env({"A": "1"})
    extra = make_env({"B": "2"})
    result = flatten_envs([base, extra], labels=["base", "extra"])
    assert result.clean
    assert len(result.entries) == 2


def test_flatten_overwrite_later_wins():
    base = make_env({"A": "old"})
    override = make_env({"A": "new"})
    result = flatten_envs([base, override], labels=["base", "override"], overwrite=True)
    values = {e.key: e.value for e in result.entries}
    assert values["A"] == "new"


def test_flatten_no_overwrite_keeps_first():
    base = make_env({"A": "first"})
    other = make_env({"A": "second"})
    result = flatten_envs([base, other], labels=["base", "other"], overwrite=False)
    values = {e.key: e.value for e in result.entries}
    assert values["A"] == "first"


def test_flatten_records_conflicts():
    base = make_env({"A": "1"})
    other = make_env({"A": "2"})
    result = flatten_envs([base, other], labels=["base", "other"])
    assert not result.clean
    assert "A" in result.conflicts
    assert len(result.conflicts["A"]) == 2


def test_flatten_merged_from_labels():
    a = make_env({"X": "1"})
    b = make_env({"Y": "2"})
    result = flatten_envs([a, b], labels=["dev", "prod"])
    assert result.merged_from == ["dev", "prod"]


def test_to_flattened_dotenv_format():
    env = make_env({"KEY": "val", "OTHER": "x"})
    result = flatten_envs([env])
    output = to_flattened_dotenv(result)
    assert "KEY=val" in output
    assert "OTHER=x" in output
    assert output.endswith("\n")
