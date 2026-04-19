import pytest
from envpatch.parser import EnvFile
from envpatch.prune import prune_env, to_pruned_dotenv


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_prune_empty_values_by_default():
    env = make_env("FOO=bar\nBAZ=\nQUX=hello\n")
    result = prune_env(env)
    keys = [e.key for e in result.kept]
    assert "FOO" in keys
    assert "QUX" in keys
    assert "BAZ" not in keys
    assert len(result.removed) == 1


def test_prune_keep_empty_when_disabled():
    env = make_env("FOO=\nBAR=value\n")
    result = prune_env(env, remove_empty=False)
    assert result.clean
    assert len(result.kept) == 2


def test_prune_explicit_keys():
    env = make_env("FOO=bar\nSECRET=abc\nBAZ=qux\n")
    result = prune_env(env, remove_empty=False, keys=["SECRET"])
    keys = [e.key for e in result.kept]
    assert "SECRET" not in keys
    assert "FOO" in keys
    assert "BAZ" in keys


def test_prune_clean_flag_when_nothing_removed():
    env = make_env("FOO=bar\nBAZ=qux\n")
    result = prune_env(env)
    assert result.clean


def test_prune_not_clean_when_entries_removed():
    env = make_env("FOO=\n")
    result = prune_env(env)
    assert not result.clean


def test_to_pruned_dotenv_serializes_kept_entries():
    env = make_env("FOO=bar\nEMPTY=\nBAZ=qux\n")
    result = prune_env(env)
    output = to_pruned_dotenv(result)
    assert "FOO=bar" in output
    assert "BAZ=qux" in output
    assert "EMPTY" not in output


def test_prune_multiple_explicit_keys():
    env = make_env("A=1\nB=2\nC=3\n")
    result = prune_env(env, remove_empty=False, keys=["A", "C"])
    keys = [e.key for e in result.kept]
    assert keys == ["B"]
    assert len(result.removed) == 2
