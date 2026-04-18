import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.sort import sort_env, to_sorted_dotenv, SortResult


def make_env(*pairs) -> EnvFile:
    entries = [EnvEntry(key=k, value=v) for k, v in pairs]
    return EnvFile(entries=entries)


def test_sort_ascending():
    env = make_env(("ZEBRA", "1"), ("APPLE", "2"), ("MANGO", "3"))
    result = sort_env(env)
    keys = [e.key for e in result.sorted_entries]
    assert keys == ["APPLE", "MANGO", "ZEBRA"]


def test_sort_descending():
    env = make_env(("ZEBRA", "1"), ("APPLE", "2"), ("MANGO", "3"))
    result = sort_env(env, reverse=True)
    keys = [e.key for e in result.sorted_entries]
    assert keys == ["ZEBRA", "MANGO", "APPLE"]


def test_already_sorted_changed_false():
    env = make_env(("ALPHA", "1"), ("BETA", "2"), ("GAMMA", "3"))
    result = sort_env(env)
    assert not result.changed


def test_unsorted_changed_true():
    env = make_env(("GAMMA", "3"), ("ALPHA", "1"))
    result = sort_env(env)
    assert result.changed


def test_group_prefix_sorts_within_groups():
    env = make_env(
        ("DB_PORT", "5432"),
        ("APP_NAME", "myapp"),
        ("DB_HOST", "localhost"),
        ("APP_ENV", "prod"),
    )
    result = sort_env(env, group_prefix=True)
    keys = [e.key for e in result.sorted_entries]
    assert keys.index("APP_ENV") < keys.index("APP_NAME")
    assert keys.index("DB_HOST") < keys.index("DB_PORT")
    app_pos = min(keys.index("APP_ENV"), keys.index("APP_NAME"))
    db_pos = min(keys.index("DB_HOST"), keys.index("DB_PORT"))
    assert app_pos < db_pos


def test_to_sorted_dotenv_output():
    env = make_env(("ZEBRA", "z"), ("ALPHA", "a"))
    result = sort_env(env)
    output = to_sorted_dotenv(result)
    lines = output.strip().splitlines()
    assert lines[0] == "ALPHA=a"
    assert lines[1] == "ZEBRA=z"


def test_to_sorted_dotenv_empty():
    env = EnvFile(entries=[])
    result = sort_env(env)
    assert to_sorted_dotenv(result) == ""
