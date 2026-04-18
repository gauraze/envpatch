"""Tests for envpatch.lint."""
import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.lint import lint_env_file, LintIssue


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_clean_env_passes():
    env = make_env({"HOST": "localhost", "PORT": "8080"})
    result = lint_env_file(env)
    assert result.ok
    assert result.issues == []


def test_lowercase_key_warning():
    env = make_env({"host": "localhost"})
    result = lint_env_file(env)
    assert any(i.key == "host" and "uppercase" in i.message for i in result.warnings)


def test_key_with_spaces_is_error():
    env = make_env({"MY KEY": "value"})
    result = lint_env_file(env)
    assert any(i.severity == "error" and "spaces" in i.message for i in result.issues)
    assert not result.ok


def test_leading_underscore_warning():
    env = make_env({"_SECRET": "abc"})
    result = lint_env_file(env)
    assert any("underscore" in i.message for i in result.warnings)


def test_value_with_whitespace_warning():
    env = make_env({"KEY": " value "})
    result = lint_env_file(env)
    assert any("whitespace" in i.message for i in result.warnings)


def test_value_with_newline_is_error():
    env = make_env({"KEY": "line1\nline2"})
    result = lint_env_file(env)
    assert any(i.severity == "error" and "newline" in i.message for i in result.issues)


def test_strict_mode_promotes_warnings_to_errors():
    env = make_env({"lower": "val"})
    result = lint_env_file(env, strict=True)
    assert all(i.severity == "error" for i in result.issues)
    assert not result.ok


def test_lint_issue_str():
    issue = LintIssue(key="FOO", message="test message", severity="warning")
    assert str(issue) == "[WARNING] FOO: test message"
