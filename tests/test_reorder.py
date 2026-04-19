import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.reorder import reorder_env


def make_env(pairs: list[tuple[str, str]]) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(entries=entries)


def test_reorder_basic_order():
    env = make_env([("C", "3"), ("A", "1"), ("B", "2")])
    result = reorder_env(env, order=["A", "B", "C"])
    assert [e.key for e in result.entries] == ["A", "B", "C"]


def test_reorder_partial_order_appends_remaining():
    env = make_env([("C", "3"), ("A", "1"), ("B", "2")])
    result = reorder_env(env, order=["B"], append_remaining=True)
    keys = [e.key for e in result.entries]
    assert keys[0] == "B"
    assert set(keys) == {"A", "B", "C"}


def test_reorder_drop_remaining_when_flag_false():
    env = make_env([("A", "1"), ("B", "2"), ("C", "3")])
    result = reorder_env(env, order=["A"], append_remaining=False)
    assert [e.key for e in result.entries] == ["A"]


def test_reorder_clean_when_already_ordered():
    env = make_env([("A", "1"), ("B", "2"), ("C", "3")])
    result = reorder_env(env, order=["A", "B", "C"])
    assert result.clean() is True


def test_reorder_not_clean_when_moved():
    env = make_env([("B", "2"), ("A", "1")])
    result = reorder_env(env, order=["A", "B"])
    assert result.clean() is False


def test_reorder_unknown_keys_in_order_ignored():
    env = make_env([("A", "1"), ("B", "2")])
    result = reorder_env(env, order=["Z", "A", "B"])
    assert [e.key for e in result.entries] == ["A", "B"]


def test_to_dotenv_output():
    env = make_env([("B", "2"), ("A", "1")])
    result = reorder_env(env, order=["A", "B"])
    output = result.to_dotenv()
    assert output == "A=1\nB=2\n"


def test_reorder_empty_env():
    """Reordering an empty EnvFile should return an empty EnvFile without error."""
    env = make_env([])
    result = reorder_env(env, order=["A", "B"])
    assert result.entries == []


def test_reorder_empty_order_appends_remaining():
    """An empty order with append_remaining=True should preserve all entries."""
    env = make_env([("A", "1"), ("B", "2")])
    result = reorder_env(env, order=[], append_remaining=True)
    assert {e.key for e in result.entries} == {"A", "B"}
