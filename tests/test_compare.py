"""Tests for envpatch.compare module."""
import pytest
from envpatch.parser import EnvFile
from envpatch.compare import compare_envs, compare_summary, CompareResult
from envpatch.diff import ChangeType


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_compare_identical_envs():
    env = make_env("FOO=bar\nBAZ=qux\n")
    result = compare_envs(env, env, include_unchanged=True)
    assert result.is_identical
    assert len(result.unchanged) == 2


def test_compare_added_key():
    base = make_env("FOO=bar\n")
    other = make_env("FOO=bar\nNEW=val\n")
    result = compare_envs(base, other)
    assert len(result.added) == 1
    assert result.added[0].key == "NEW"


def test_compare_removed_key():
    base = make_env("FOO=bar\nOLD=gone\n")
    other = make_env("FOO=bar\n")
    result = compare_envs(base, other)
    assert len(result.removed) == 1
    assert result.removed[0].key == "OLD"


def test_compare_modified_key():
    base = make_env("FOO=old\n")
    other = make_env("FOO=new\n")
    result = compare_envs(base, other)
    assert len(result.modified) == 1
    assert result.modified[0].old_value == "old"
    assert result.modified[0].new_value == "new"


def test_compare_names_stored():
    env = make_env("A=1\n")
    result = compare_envs(env, env, base_name="dev", other_name="prod")
    assert result.base_name == "dev"
    assert result.other_name == "prod"


def test_compare_summary_counts():
    base = make_env("A=1\nB=2\nC=3\n")
    other = make_env("A=1\nB=changed\nD=4\n")
    result = compare_envs(base, other, include_unchanged=True)
    s = compare_summary(result)
    assert s["added"] == 1
    assert s["removed"] == 1
    assert s["modified"] == 1
    assert s["unchanged"] == 1


def test_is_identical_false_when_diff():
    base = make_env("X=1\n")
    other = make_env("X=2\n")
    result = compare_envs(base, other)
    assert not result.is_identical
