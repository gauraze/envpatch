import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.rename import rename_keys


def make_env(**kwargs) -> EnvFile:
    return EnvFile(entries=[EnvEntry(key=k, value=v) for k, v in kwargs.items()])


def test_rename_single_key():
    env = make_env(OLD_KEY="value")
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
    assert result.clean
    assert len(result.renamed) == 1
    assert result.renamed[0] == ("OLD_KEY", "NEW_KEY")
    assert result.output.get("NEW_KEY") == "value"
    assert result.output.get("OLD_KEY") is None


def test_rename_preserves_other_keys():
    env = make_env(A="1", B="2", C="3")
    result = rename_keys(env, {"B": "BETA"})
    assert result.output.get("A") == "1"
    assert result.output.get("BETA") == "2"
    assert result.output.get("C") == "3"


def test_rename_conflict_skipped_without_overwrite():
    env = make_env(OLD="val", NEW="existing")
    result = rename_keys(env, {"OLD": "NEW"})
    assert not result.clean
    assert len(result.skipped) == 1
    assert result.skipped[0][0] == "OLD"
    assert result.output.get("OLD") == "val"  # unchanged


def test_rename_conflict_overwrite():
    env = make_env(OLD="val", NEW="existing")
    result = rename_keys(env, {"OLD": "NEW"}, overwrite=True)
    assert result.clean
    assert result.output.get("NEW") == "val"


def test_rename_multiple_keys():
    env = make_env(A="1", B="2", C="3")
    result = rename_keys(env, {"A": "ALPHA", "C": "GAMMA"})
    assert len(result.renamed) == 2
    assert result.output.get("ALPHA") == "1"
    assert result.output.get("GAMMA") == "3"
    assert result.output.get("B") == "2"


def test_rename_preserves_comment():
    entry = EnvEntry(key="OLD", value="v", comment="# my comment")
    env = EnvFile(entries=[entry])
    result = rename_keys(env, {"OLD": "NEW"})
    new_entry = next(e for e in result.output.entries if e.key == "NEW")
    assert new_entry.comment == "# my comment"
