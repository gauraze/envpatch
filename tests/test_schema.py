"""Tests for envpatch.schema."""
import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.schema import (
    SchemaField, load_schema, validate_against_schema, SchemaResult
)


def make_env(**kwargs) -> EnvFile:
    entries = [EnvEntry(k, v) for k, v in kwargs.items()]
    return EnvFile(entries)


def test_valid_env_passes():
    schema = [SchemaField(key="PORT", required=True)]
    env = make_env(PORT="8080")
    result = validate_against_schema(env, schema)
    assert result.valid


def test_missing_required_key():
    schema = [SchemaField(key="SECRET", required=True)]
    env = make_env(PORT="8080")
    result = validate_against_schema(env, schema)
    assert not result.valid
    assert any("missing" in str(v) for v in result.violations)


def test_missing_optional_key_passes():
    schema = [SchemaField(key="OPTIONAL", required=False)]
    env = make_env(PORT="8080")
    result = validate_against_schema(env, schema)
    assert result.valid


def test_allowed_values_violation():
    schema = [SchemaField(key="ENV", allowed_values=["production", "staging"])]
    env = make_env(ENV="dev")
    result = validate_against_schema(env, schema)
    assert not result.valid
    assert any("allowed" in str(v) for v in result.violations)


def test_allowed_values_passes():
    schema = [SchemaField(key="ENV", allowed_values=["production", "staging"])]
    env = make_env(ENV="staging")
    result = validate_against_schema(env, schema)
    assert result.valid


def test_pattern_violation():
    schema = [SchemaField(key="PORT", pattern=r"\d+")]
    env = make_env(PORT="abc")
    result = validate_against_schema(env, schema)
    assert not result.valid
    assert any("pattern" in str(v) for v in result.violations)


def test_pattern_passes():
    schema = [SchemaField(key="PORT", pattern=r"\d+")]
    env = make_env(PORT="3000")
    result = validate_against_schema(env, schema)
    assert result.valid


def test_load_schema_from_dict():
    data = {
        "DATABASE_URL": {"required": True, "description": "Postgres URL"},
        "DEBUG": {"required": False, "allowed_values": ["true", "false"]},
    }
    fields = load_schema(data)
    assert len(fields) == 2
    keys = [f.key for f in fields]
    assert "DATABASE_URL" in keys
    assert "DEBUG" in keys


def test_violation_str():
    from envpatch.schema import SchemaViolation
    v = SchemaViolation(key="FOO", message="required key is missing")
    assert "FOO" in str(v)
    assert "missing" in str(v)
