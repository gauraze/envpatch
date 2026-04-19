import pytest
from envpatch.parser import EnvFile
from envpatch.required import check_required, assert_required, RequiredViolation


def make_env(content: str) -> EnvFile:
    return EnvFile.parse(content)


def test_all_keys_present_clean():
    env = make_env("FOO=bar\nBAZ=qux\n")
    result = check_required(env, ["FOO", "BAZ"])
    assert result.clean
    assert result.violations == []


def test_missing_key_violation():
    env = make_env("FOO=bar\n")
    result = check_required(env, ["FOO", "MISSING"])
    assert not result.clean
    assert len(result.violations) == 1
    assert result.violations[0].key == "MISSING"
    assert "not present" in result.violations[0].reason


def test_empty_value_violation_by_default():
    env = make_env("FOO=\n")
    result = check_required(env, ["FOO"])
    assert not result.clean
    assert result.violations[0].key == "FOO"
    assert "empty" in result.violations[0].reason


def test_empty_value_allowed_when_flag_set():
    env = make_env("FOO=\n")
    result = check_required(env, ["FOO"], allow_empty=True)
    assert result.clean


def test_multiple_violations():
    env = make_env("A=1\n")
    result = check_required(env, ["A", "B", "C"])
    assert len(result.violations) == 2
    keys = {v.key for v in result.violations}
    assert keys == {"B", "C"}


def test_violation_str():
    v = RequiredViolation(key="SECRET", reason="key not present")
    assert "SECRET" in str(v)
    assert "key not present" in str(v)


def test_assert_required_raises_on_missing():
    env = make_env("FOO=bar\n")
    with pytest.raises(ValueError, match="Required key violations"):
        assert_required(env, ["FOO", "MISSING"])


def test_assert_required_passes_when_clean():
    env = make_env("FOO=bar\nBAR=baz\n")
    assert_required(env, ["FOO", "BAR"])  # should not raise
