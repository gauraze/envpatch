import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.align import align_env, to_aligned_dotenv


def make_env(pairs):
    entries = [
        EnvEntry(key=k, value=v, raw=f"{k}={v}", comment=None)
        for k, v in pairs
    ]
    return EnvFile(entries=entries)


def test_align_pads_shorter_keys():
    env = make_env([("A", "1"), ("LONG_KEY", "2")])
    result = align_env(env)
    assert result.changed
    raws = [e.raw for e in result.entries if e.key]
    assert raws[0] == "A       =1"
    assert raws[1] == "LONG_KEY=2"


def test_align_already_aligned_not_changed():
    entries = [
        EnvEntry(key="AB", value="1", raw="AB=1", comment=None),
        EnvEntry(key="CD", value="2", raw="CD=2", comment=None),
    ]
    env = EnvFile(entries=entries)
    result = align_env(env)
    assert not result.changed
    assert result.padded_keys == []


def test_align_empty_env():
    env = EnvFile(entries=[])
    result = align_env(env)
    assert not result.changed
    assert result.entries == []


def test_align_single_key_no_change():
    env = make_env([("KEY", "val")])
    result = align_env(env)
    assert not result.changed


def test_align_records_padded_keys():
    env = make_env([("X", "1"), ("LONG", "2")])
    result = align_env(env)
    assert "X" in result.padded_keys
    assert "LONG" not in result.padded_keys


def test_to_aligned_dotenv_output():
    env = make_env([("A", "hello"), ("BB", "world")])
    result = align_env(env)
    out = to_aligned_dotenv(result)
    lines = out.strip().splitlines()
    eq_positions = [l.index("=") for l in lines]
    assert len(set(eq_positions)) == 1


def test_align_skips_comment_entries():
    entries = [
        EnvEntry(key=None, value=None, raw="# comment", comment="# comment"),
        EnvEntry(key="SHORT", value="x", raw="SHORT=x", comment=None),
        EnvEntry(key="MUCH_LONGER", value="y", raw="MUCH_LONGER=y", comment=None),
    ]
    env = EnvFile(entries=entries)
    result = align_env(env)
    assert result.changed
    comment_entry = result.entries[0]
    assert comment_entry.raw == "# comment"
