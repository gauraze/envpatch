import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.placeholder import check_placeholders, PlaceholderIssue


def make_env(pairs):
    entries = [EnvEntry(key=k, value=v, comment=None, raw=f"{k}={v}") for k, v in pairs]
    return EnvFile(entries=entries)


def test_clean_env_no_issues():
    env = make_env([("HOST", "localhost"), ("PORT", "5432")])
    result = check_placeholders(env)
    assert result.clean
    assert result.issues == []


def test_changeme_detected():
    env = make_env([("SECRET", "CHANGEME")])
    result = check_placeholders(env)
    assert not result.clean
    assert result.issues[0].key == "SECRET"


def test_template_braces_detected():
    env = make_env([("API_KEY", "{{API_KEY}}")])
    result = check_placeholders(env)
    assert not result.clean
    assert "{{" in result.issues[0].reason


def test_angle_bracket_detected():
    env = make_env([("DB_PASS", "<password>")])
    result = check_placeholders(env)
    assert not result.clean


def test_todo_detected():
    env = make_env([("TOKEN", "TODO")])
    result = check_placeholders(env)
    assert not result.clean


def test_empty_value_not_flagged():
    env = make_env([("OPTIONAL", "")])
    result = check_placeholders(env)
    assert result.clean


def test_key_filter_limits_check():
    env = make_env([("A", "CHANGEME"), ("B", "CHANGEME")])
    result = check_placeholders(env, keys=["A"])
    assert len(result.issues) == 1
    assert result.issues[0].key == "A"


def test_custom_pattern():
    env = make_env([("X", "OVERRIDE_ME")])
    result = check_placeholders(env, patterns=["OVERRIDE_ME"])
    assert not result.clean


def test_to_dotenv_output():
    env = make_env([("A", "1"), ("B", "2")])
    result = check_placeholders(env)
    assert result.to_dotenv() == "A=1\nB=2"
