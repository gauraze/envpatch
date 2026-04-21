"""Tests for envpatch.chain — chained transformation pipeline."""
import pytest

from envpatch.parser import EnvFile, EnvEntry
from envpatch.chain import (
    ChainStep,
    ChainResult,
    build_chain,
    run_chain,
)


def make_env(**kwargs: str) -> EnvFile:
    entries = [EnvEntry(key=k, value=v, raw=f"{k}={v}") for k, v in kwargs.items()]
    return EnvFile(entries=entries)


def uppercase_keys(env: EnvFile) -> EnvFile:
    """Transform: uppercase all keys."""
    new_entries = [
        EnvEntry(key=e.key.upper(), value=e.value, raw=f"{e.key.upper()}={e.value}")
        for e in env.entries
    ]
    return EnvFile(entries=new_entries)


def prefix_values(env: EnvFile) -> EnvFile:
    """Transform: prefix every value with 'PRE_'."""
    new_entries = [
        EnvEntry(key=e.key, value=f"PRE_{e.value}", raw=f"{e.key}=PRE_{e.value}")
        for e in env.entries
    ]
    return EnvFile(entries=new_entries)


def always_fails(env: EnvFile) -> EnvFile:
    raise ValueError("intentional failure")


# ---------------------------------------------------------------------------


def test_build_chain_returns_steps():
    steps = build_chain([("upper", uppercase_keys), ("prefix", prefix_values)])
    assert len(steps) == 2
    assert steps[0].name == "upper"
    assert steps[1].name == "prefix"


def test_run_chain_applies_all_steps():
    env = make_env(db_host="localhost", db_port="5432")
    steps = build_chain([("upper", uppercase_keys), ("prefix", prefix_values)])
    result = run_chain(env, steps)

    keys = [e.key for e in result.env.entries]
    values = [e.value for e in result.env.entries]

    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert all(v.startswith("PRE_") for v in values)
    assert result.steps_applied == ["upper", "prefix"]
    assert result.steps_skipped == []
    assert result.clean is True


def test_run_chain_skips_failing_step():
    env = make_env(key="value")
    steps = build_chain([("upper", uppercase_keys), ("fail", always_fails)])
    result = run_chain(env, steps)

    assert "upper" in result.steps_applied
    assert "fail" in result.steps_skipped
    assert result.clean is False


def test_run_chain_empty_steps_returns_original():
    env = make_env(foo="bar")
    result = run_chain(env, [])
    assert result.env is env
    assert result.steps_applied == []
    assert result.steps_skipped == []


def test_chain_result_summary_applied_only():
    env = make_env(x="1")
    steps = build_chain([("upper", uppercase_keys)])
    result = run_chain(env, steps)
    assert "Applied" in result.summary()
    assert "Skipped" not in result.summary()


def test_chain_result_summary_no_steps():
    env = make_env(x="1")
    result = run_chain(env, [])
    assert result.summary() == "No steps configured."


def test_run_chain_non_value_error_propagates():
    def boom(env: EnvFile) -> EnvFile:
        raise RuntimeError("unexpected")

    env = make_env(x="1")
    steps = build_chain([("boom", boom)])
    with pytest.raises(RuntimeError, match="unexpected"):
        run_chain(env, steps)
