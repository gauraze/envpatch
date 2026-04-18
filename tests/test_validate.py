"""Tests for envpatch.validate module."""
import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.diff import DiffEntry, ChangeType
from envpatch.validate import (
    validate_env_file,
    validate_patch,
    ValidationResult,
    ValidationIssue,
)


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(k, v) for k, v in pairs.items()]
    return EnvFile(entries)


def test_valid_env_passes():
    env = make_env({"HOST": "localhost", "PORT": "5432"})
    result = validate_env_file(env)
    assert result.valid
    assert result.issues == []


def test_empty_value_warning():
    env = make_env({"HOST": ""})
    result = validate_env_file(env)
    assert any(i.key == "HOST" for i in result.warnings)


def test_empty_important_key_is_error():
    env = make_env({"SECRET_KEY": ""})
    result = validate_env_file(env)
    assert not result.valid
    assert any(i.key == "SECRET_KEY" and i.severity == "error" for i in result.issues)


def test_lowercase_key_warning():
    env = make_env({"myKey": "value"})
    result = validate_env_file(env)
    assert any(i.key == "myKey" and i.severity == "warning" for i in result.issues)


def test_key_with_space_is_error():
    env = make_env({"MY KEY": "value"})
    result = validate_env_file(env)
    assert not result.valid
    assert any(i.key == "MY KEY" and i.severity == "error" for i in result.issues)


def test_patch_removes_critical_key_warns():
    changes = [DiffEntry("SECRET_KEY", ChangeType.REMOVED, old_value="abc", new_value=None)]
    target = make_env({"SECRET_KEY": "abc"})
    result = validate_patch(changes, target)
    assert any(i.key == "SECRET_KEY" and i.severity == "warning" for i in result.issues)


def test_patch_adds_empty_value_warns():
    changes = [DiffEntry("NEW_KEY", ChangeType.ADDED, old_value=None, new_value="")]
    target = make_env({})
    result = validate_patch(changes, target)
    assert any(i.key == "NEW_KEY" and i.severity == "warning" for i in result.issues)


def test_validation_result_str_no_issues():
    result = ValidationResult()
    assert "passed" in str(result)


def test_validation_issue_str():
    issue = ValidationIssue("FOO", "Something wrong.", "error")
    assert "ERROR" in str(issue)
    assert "FOO" in str(issue)
