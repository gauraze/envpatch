"""Tests for envpatch.template."""
from __future__ import annotations
from envpatch.parser import EnvFile
from envpatch.template import to_template, missing_keys, extra_keys, check_template


def make_env(text: str) -> EnvFile:
    return EnvFile.parse(text)


def test_to_template_masks_values():
    env = make_env("DB_HOST=localhost\nDB_PORT=5432\n")
    result = to_template(env)
    assert "DB_HOST=" in result
    assert "localhost" not in result
    assert "DB_PORT=" in result
    assert "5432" not in result


def test_to_template_custom_placeholder():
    env = make_env("API_KEY=secret\n")
    result = to_template(env, placeholder="CHANGEME")
    assert "API_KEY=CHANGEME" in result


def test_to_template_keep_values():
    env = make_env("HOST=prod.example.com\n")
    result = to_template(env, mask_values=False)
    assert "HOST=prod.example.com" in result


def test_missing_keys_detected():
    template = make_env("A=1\nB=2\nC=3\n")
    target = make_env("A=x\n")
    assert missing_keys(template, target) == ["B", "C"]


def test_extra_keys_detected():
    template = make_env("A=1\n")
    target = make_env("A=x\nZ=extra\n")
    assert extra_keys(template, target) == ["Z"]


def test_no_missing_no_extra():
    env = make_env("X=1\nY=2\n")
    report = check_template(env, env)
    assert report["missing"] == []
    assert report["extra"] == []


def test_check_template_returns_both():
    template = make_env("A=1\nB=2\n")
    target = make_env("A=x\nC=new\n")
    report = check_template(template, target)
    assert "B" in report["missing"]
    assert "C" in report["extra"]
