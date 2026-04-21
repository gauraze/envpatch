"""Tests for envpatch.squash."""
import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.squash import squash_envs, SquashResult


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_squash_single_file_no_conflicts():
    env = make_env({"A": "1", "B": "2"})
    result = squash_envs([env], ["base"])
    assert result.clean
    assert len(result.entries) == 2
    assert result.conflicts == {}


def test_squash_two_files_no_overlap():
    a = make_env({"A": "1"})
    b = make_env({"B": "2"})
    result = squash_envs([a, b], ["a", "b"])
    assert result.clean
    keys = [e.key for e in result.entries]
    assert "A" in keys
    assert "B" in keys


def test_squash_last_wins_on_conflict():
    a = make_env({"KEY": "old"})
    b = make_env({"KEY": "new"})
    result = squash_envs([a, b], ["a", "b"], last_wins=True)
    assert not result.clean
    assert "KEY" in result.conflicts
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.value == "new"
    assert result.sources["KEY"] == "b"


def test_squash_first_wins_on_conflict():
    a = make_env({"KEY": "first"})
    b = make_env({"KEY": "second"})
    result = squash_envs([a, b], ["a", "b"], last_wins=False)
    assert not result.clean
    entry = next(e for e in result.entries if e.key == "KEY")
    assert entry.value == "first"
    assert result.sources["KEY"] == "a"


def test_squash_same_value_not_a_conflict():
    a = make_env({"KEY": "same"})
    b = make_env({"KEY": "same"})
    result = squash_envs([a, b], ["a", "b"])
    assert result.clean
    assert result.conflicts == {}


def test_squash_to_dotenv_format():
    env = make_env({"X": "1", "Y": "2"})
    result = squash_envs([env])
    dotenv = result.to_dotenv()
    assert "X=1" in dotenv
    assert "Y=2" in dotenv


def test_squash_mismatched_filenames_raises():
    env = make_env({"A": "1"})
    with pytest.raises(ValueError):
        squash_envs([env], ["a", "b"])


def test_squash_three_files_tracks_all_conflicts():
    a = make_env({"K": "v1"})
    b = make_env({"K": "v2"})
    c = make_env({"K": "v3"})
    result = squash_envs([a, b, c], ["a", "b", "c"], last_wins=True)
    assert not result.clean
    assert len(result.conflicts["K"]) >= 2
    entry = next(e for e in result.entries if e.key == "K")
    assert entry.value == "v3"
