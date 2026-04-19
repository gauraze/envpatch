import pytest
from envpatch.parser import EnvFile
from envpatch.transform import apply_transforms, to_transformed_dotenv, TransformResult


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_uppercase_all_keys():
    env = make_env("FOO=hello\nBAR=world\n")
    result = apply_transforms(env, {"*": str.upper})
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["FOO"] == "HELLO"
    assert values["BAR"] == "WORLD"
    assert set(result.changed_keys) == {"FOO", "BAR"}


def test_uppercase_specific_key():
    env = make_env("FOO=hello\nBAR=world\n")
    result = apply_transforms(env, {"FOO": str.upper})
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["FOO"] == "HELLO"
    assert values["BAR"] == "world"
    assert result.changed_keys == ["FOO"]


def test_no_change_when_already_transformed():
    env = make_env("FOO=HELLO\n")
    result = apply_transforms(env, {"FOO": str.upper})
    assert result.clean
    assert result.changed_keys == []


def test_strip_whitespace():
    env = make_env("FOO=  spaced  \n")
    result = apply_transforms(env, {"FOO": str.strip})
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["FOO"] == "spaced"


def test_keys_filter_limits_transform():
    env = make_env("FOO=hello\nBAR=world\n")
    result = apply_transforms(env, {"*": str.upper}, keys=["FOO"])
    values = {e.key: e.value for e in result.entries if e.key}
    assert values["FOO"] == "HELLO"
    assert values["BAR"] == "world"


def test_to_transformed_dotenv_output():
    env = make_env("FOO=hello\nBAR=world\n")
    result = apply_transforms(env, {"FOO": str.upper})
    output = to_transformed_dotenv(result)
    assert "FOO=HELLO" in output
    assert "BAR=world" in output


def test_clean_flag_false_when_changed():
    env = make_env("FOO=hello\n")
    result = apply_transforms(env, {"FOO": str.upper})
    assert not result.clean
