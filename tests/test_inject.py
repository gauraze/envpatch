"""Tests for envpatch.inject."""
from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest

from envpatch.parser import EnvFile, EnvEntry
from envpatch.inject import inject_env, run_with_env


def make_env(pairs: dict) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in pairs.items()]
    return EnvFile(entries=entries)


def test_inject_adds_new_keys():
    ef = make_env({"NEW_KEY": "hello"})
    env, result = inject_env(ef, overwrite=False)
    assert env["NEW_KEY"] == "hello"
    assert "NEW_KEY" in result.injected
    assert result.clean


def test_inject_skips_existing_without_overwrite():
    ef = make_env({"PATH": "/custom"})
    env, result = inject_env(ef, overwrite=False)
    assert env["PATH"] != "/custom"
    assert "PATH" in result.skipped
    assert not result.clean


def test_inject_overwrites_when_flag_set():
    ef = make_env({"PATH": "/custom"})
    env, result = inject_env(ef, overwrite=True)
    assert env["PATH"] == "/custom"
    assert "PATH" in result.injected


def test_inject_subset_of_keys():
    ef = make_env({"A": "1", "B": "2", "C": "3"})
    env, result = inject_env(ef, keys=["A", "C"])
    assert "A" in result.injected
    assert "C" in result.injected
    assert "B" not in result.injected
    assert "B" not in result.skipped


def test_run_with_env_returns_returncode():
    ef = make_env({"ENVPATCH_TEST": "1"})
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    with patch("envpatch.inject.subprocess.run", return_value=mock_proc) as mock_run:
        result = run_with_env(ef, ["echo", "hi"])
    assert result.returncode == 0
    call_env = mock_run.call_args.kwargs["env"]
    assert call_env["ENVPATCH_TEST"] == "1"


def test_run_with_env_propagates_nonzero_exit():
    ef = make_env({"X": "y"})
    mock_proc = MagicMock()
    mock_proc.returncode = 42
    with patch("envpatch.inject.subprocess.run", return_value=mock_proc):
        result = run_with_env(ef, ["false"])
    assert result.returncode == 42
