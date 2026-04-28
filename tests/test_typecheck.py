from __future__ import annotations

import pytest

from click.testing import CliRunner

from envpatch.parser import EnvFile
from envpatch.typecheck import typecheck_env, TypeViolation
from envpatch.cli_typecheck import typecheck_check


def make_env(raw: str) -> EnvFile:
    return EnvFile.parse(raw)


# ---------------------------------------------------------------------------
# Unit tests
# ---------------------------------------------------------------------------

def test_valid_int_passes():
    env = make_env("PORT=8080\n")
    result = typecheck_env(env, {"PORT": "int"})
    assert result.clean
    assert "PORT" in result.checked


def test_invalid_int_raises_violation():
    env = make_env("PORT=abc\n")
    result = typecheck_env(env, {"PORT": "int"})
    assert not result.clean
    assert len(result.violations) == 1
    assert result.violations[0].key == "PORT"
    assert result.violations[0].expected == "int"


def test_valid_float_passes():
    env = make_env("RATIO=3.14\n")
    result = typecheck_env(env, {"RATIO": "float"})
    assert result.clean


def test_invalid_float_raises_violation():
    env = make_env("RATIO=not-a-float\n")
    result = typecheck_env(env, {"RATIO": "float"})
    assert not result.clean


def test_bool_true_variants_pass():
    for val in ["true", "True", "1", "yes", "false", "False", "0", "no"]:
        env = make_env(f"FLAG={val}\n")
        result = typecheck_env(env, {"FLAG": "bool"})
        assert result.clean, f"Expected {val!r} to pass bool check"


def test_invalid_bool_raises_violation():
    env = make_env("FLAG=maybe\n")
    result = typecheck_env(env, {"FLAG": "bool"})
    assert not result.clean
    assert "boolean" in result.violations[0].reason


def test_str_type_always_passes():
    env = make_env("NAME=anything goes 123!\n")
    result = typecheck_env(env, {"NAME": "str"})
    assert result.clean


def test_missing_key_ignored():
    env = make_env("FOO=bar\n")
    result = typecheck_env(env, {"MISSING": "int"})
    assert result.clean
    assert "MISSING" not in result.checked


def test_unsupported_type_is_violation():
    env = make_env("X=hello\n")
    result = typecheck_env(env, {"X": "uuid"})
    assert not result.clean
    assert "unsupported type" in result.violations[0].reason


def test_violation_str_representation():
    v = TypeViolation(key="PORT", expected="int", actual_value="abc", reason="not a valid integer")
    text = str(v)
    assert "PORT" in text
    assert "int" in text
    assert "abc" in text


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def runner():
    return CliRunner()


def test_cli_check_passes(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nDEBUG=true\n")
    result = runner.invoke(
        typecheck_check,
        [str(env_file), "--types", '{"PORT":"int","DEBUG":"bool"}'],
    )
    assert result.exit_code == 0
    assert "passed" in result.output


def test_cli_check_fails_on_bad_value(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=notanint\n")
    result = runner.invoke(
        typecheck_check,
        [str(env_file), "--types", '{"PORT":"int"}'],
    )
    assert result.exit_code == 1


def test_cli_check_invalid_json_exits_2(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\n")
    result = runner.invoke(
        typecheck_check,
        [str(env_file), "--types", "not-json"],
    )
    assert result.exit_code == 2


def test_cli_quiet_suppresses_output(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=9000\n")
    result = runner.invoke(
        typecheck_check,
        [str(env_file), "--types", '{"PORT":"int"}', "--quiet"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == ""
