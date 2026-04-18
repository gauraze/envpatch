import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.dedupe import find_duplicates, dedupe_env, to_deduped_dotenv


def make_env(pairs: list) -> EnvFile:
    entries = []
    for item in pairs:
        if isinstance(item, tuple):
            k, v = item
            entries.append(EnvEntry(key=k, value=v, raw=f"{k}={v}"))
        else:
            entries.append(EnvEntry(key=None, value=None, raw=item))
    return EnvFile(entries=entries)


def test_no_duplicates_returns_clean():
    env = make_env([("A", "1"), ("B", "2")])
    result = dedupe_env(env)
    assert result.clean
    assert len(result.cleaned) == 2


def test_find_duplicates_detects_repeated_key():
    env = make_env([("A", "1"), ("B", "2"), ("A", "3")])
    dupes = find_duplicates(env)
    assert "A" in dupes
    assert len(dupes["A"]) == 2


def test_dedupe_keep_last():
    env = make_env([("A", "first"), ("B", "2"), ("A", "last")])
    result = dedupe_env(env, keep="last")
    keys = [e.key for e in result.cleaned if e.key]
    assert keys.count("A") == 1
    a_entry = next(e for e in result.cleaned if e.key == "A")
    assert a_entry.value == "last"


def test_dedupe_keep_first():
    env = make_env([("A", "first"), ("B", "2"), ("A", "last")])
    result = dedupe_env(env, keep="first")
    a_entry = next(e for e in result.cleaned if e.key == "A")
    assert a_entry.value == "first"


def test_comments_and_blanks_preserved():
    env = make_env(["# comment", ("A", "1"), "", ("A", "2")])
    result = dedupe_env(env, keep="last")
    raws = [e.raw for e in result.cleaned if e.key is None]
    assert "# comment" in raws
    assert "" in raws


def test_invalid_keep_raises():
    env = make_env([("A", "1")])
    with pytest.raises(ValueError):
        dedupe_env(env, keep="middle")


def test_to_deduped_dotenv_output():
    env = make_env([("A", "1"), ("A", "2"), ("B", "3")])
    result = dedupe_env(env, keep="last")
    output = to_deduped_dotenv(result)
    lines = output.splitlines()
    a_lines = [l for l in lines if l.startswith("A=")]
    assert len(a_lines) == 1
    assert "A=2" in a_lines
