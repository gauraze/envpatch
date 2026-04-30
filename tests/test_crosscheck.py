"""Tests for envpatch.crosscheck."""
from __future__ import annotations

import pytest

from envpatch.parser import EnvEntry, EnvFile
from envpatch.crosscheck import crosscheck_envs, CrossCheckIssue


def make_env(*pairs: tuple) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(entries=entries)


def test_both_files_have_all_keys_clean():
    a = make_env(("HOST", "localhost"), ("PORT", "5432"))
    b = make_env(("HOST", "prod.example.com"), ("PORT", "5432"))
    result = crosscheck_envs(a, b)
    assert result.clean
    assert result.checked == 2


def test_key_missing_from_a():
    a = make_env(("PORT", "5432"))
    b = make_env(("HOST", "prod.example.com"), ("PORT", "5432"))
    result = crosscheck_envs(a, b)
    assert not result.clean
    msgs = [i.message for i in result.issues]
    assert any("missing from file A" in m for m in msgs)


def test_key_missing_from_b():
    a = make_env(("HOST", "localhost"), ("PORT", "5432"))
    b = make_env(("PORT", "5432"))
    result = crosscheck_envs(a, b)
    assert not result.clean
    msgs = [i.message for i in result.issues]
    assert any("missing from file B" in m for m in msgs)


def test_empty_value_in_a_is_issue():
    a = make_env(("SECRET", ""), ("PORT", "5432"))
    b = make_env(("SECRET", "s3cr3t"), ("PORT", "5432"))
    result = crosscheck_envs(a, b)
    assert not result.clean
    issue = result.issues[0]
    assert issue.key == "SECRET"
    assert "empty in file A" in issue.message


def test_empty_value_in_b_is_issue():
    a = make_env(("SECRET", "s3cr3t"))
    b = make_env(("SECRET", ""))
    result = crosscheck_envs(a, b)
    assert not result.clean
    assert "empty in file B" in result.issues[0].message


def test_allow_empty_skips_empty_check():
    a = make_env(("SECRET", ""))
    b = make_env(("SECRET", ""))
    result = crosscheck_envs(a, b, allow_empty=True)
    assert result.clean


def test_required_keys_limits_scope():
    a = make_env(("HOST", "localhost"), ("DEBUG", "true"))
    b = make_env(("HOST", "prod.example.com"))
    # Only check HOST — DEBUG absence in B should not matter
    result = crosscheck_envs(a, b, required_keys=["HOST"])
    assert result.clean
    assert result.checked == 1


def test_required_key_missing_from_both():
    a = make_env(("PORT", "5432"))
    b = make_env(("PORT", "5432"))
    result = crosscheck_envs(a, b, required_keys=["SECRET"])
    assert not result.clean
    assert "missing from both files" in result.issues[0].message


def test_issue_str_representation():
    issue = CrossCheckIssue("KEY", None, "val", "missing from file A")
    s = str(issue)
    assert "KEY" in s
    assert "missing from file A" in s
