"""Tests for envpatch.annotate."""
from __future__ import annotations

import pytest

from envpatch.parser import EnvFile
from envpatch.annotate import annotate_env, AnnotateResult


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_annotate_single_key_inline():
    env = make_env("API_KEY=abc123\n")
    result = annotate_env(env, {"API_KEY": "your API key"}, inline=True)
    assert result.annotated == ["API_KEY"]
    dotenv = result.to_dotenv()
    assert "# your API key" in dotenv
    assert "API_KEY=abc123" in dotenv


def test_annotate_single_key_above():
    env = make_env("DB_URL=postgres://localhost/db\n")
    result = annotate_env(env, {"DB_URL": "database connection"}, inline=False)
    lines = result.to_dotenv().splitlines()
    assert lines[0] == "# database connection"
    assert lines[1].startswith("DB_URL=")


def test_unannotated_key_goes_to_skipped():
    env = make_env("FOO=bar\nBAZ=qux\n")
    result = annotate_env(env, {"FOO": "foo comment"}, inline=True)
    assert "BAZ" in result.skipped
    assert "FOO" in result.annotated


def test_clean_property_false_when_annotated():
    env = make_env("KEY=val\n")
    result = annotate_env(env, {"KEY": "a comment"})
    assert result.clean is False


def test_clean_property_true_when_nothing_annotated():
    env = make_env("KEY=val\n")
    result = annotate_env(env, {})
    assert result.clean is True


def test_overwrite_false_skips_existing_inline_comment():
    env = make_env("SECRET=hunter2  # do not share\n")
    result = annotate_env(
        env, {"SECRET": "new comment"}, overwrite=False, inline=True
    )
    assert "SECRET" in result.skipped
    assert result.annotated == []
    # Original comment preserved.
    assert "do not share" in result.to_dotenv()


def test_overwrite_true_replaces_existing_inline_comment():
    env = make_env("SECRET=hunter2  # old comment\n")
    result = annotate_env(
        env, {"SECRET": "new comment"}, overwrite=True, inline=True
    )
    assert "SECRET" in result.annotated
    dotenv = result.to_dotenv()
    assert "new comment" in dotenv
    assert "old comment" not in dotenv


def test_multiple_keys_annotated():
    env = make_env("A=1\nB=2\nC=3\n")
    result = annotate_env(env, {"A": "alpha", "C": "charlie"}, inline=True)
    assert sorted(result.annotated) == ["A", "C"]
    assert result.skipped == ["B"]
    dotenv = result.to_dotenv()
    assert "# alpha" in dotenv
    assert "# charlie" in dotenv


def test_to_dotenv_ends_with_newline():
    env = make_env("X=1\n")
    result = annotate_env(env, {"X": "ex"}, inline=True)
    assert result.to_dotenv().endswith("\n")


def test_empty_env_returns_empty_dotenv():
    env = make_env("")
    result = annotate_env(env, {"MISSING": "nope"})
    assert result.to_dotenv() == ""
    assert result.annotated == []
