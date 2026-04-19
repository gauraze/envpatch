import pytest
from envpatch.parser import EnvFile, EnvEntry
from envpatch.deprecate import deprecate_env, DeprecationWarning_, to_deprecate_dotenv


def make_env(pairs):
    entries = [EnvEntry(key=k, value=v) for k, v in pairs.items()]
    return EnvFile(entries)


def test_no_deprecated_keys_clean():
    env = make_env({"HOST": "localhost", "PORT": "8080"})
    _, result = deprecate_env(env, {"OLD_KEY": {"reason": "gone"}}, apply=False)
    assert result.clean
    assert result.warnings == []


def test_deprecated_key_warns():
    env = make_env({"OLD_HOST": "localhost", "PORT": "8080"})
    _, result = deprecate_env(env, {"OLD_HOST": {"reason": "use HOST", "replacement": "HOST"}}, apply=False)
    assert not result.clean
    assert len(result.warnings) == 1
    assert result.warnings[0].key == "OLD_HOST"
    assert "HOST" in str(result.warnings[0])


def test_apply_renames_key():
    env = make_env({"OLD_HOST": "localhost"})
    new_env, result = deprecate_env(
        env,
        {"OLD_HOST": {"reason": "renamed", "replacement": "HOST", "drop": False}},
        apply=True,
    )
    assert "HOST" in new_env.keys()
    assert "OLD_HOST" not in new_env.keys()
    assert result.renamed == {"OLD_HOST": "HOST"}


def test_apply_drops_key():
    env = make_env({"LEGACY": "val", "KEEP": "yes"})
    new_env, result = deprecate_env(
        env,
        {"LEGACY": {"reason": "removed", "drop": True}},
        apply=True,
    )
    assert "LEGACY" not in new_env.keys()
    assert "KEEP" in new_env.keys()
    assert "LEGACY" in result.dropped


def test_apply_false_does_not_mutate():
    env = make_env({"OLD": "val"})
    new_env, result = deprecate_env(
        env,
        {"OLD": {"reason": "gone", "replacement": "NEW", "drop": False}},
        apply=False,
    )
    assert "OLD" in new_env.keys()
    assert result.renamed == {}


def test_warning_str_no_replacement():
    w = DeprecationWarning_("OLD", "no longer used")
    assert "OLD" in str(w)
    assert "no longer used" in str(w)
    assert "->" not in str(w)


def test_to_deprecate_dotenv():
    env = make_env({"A": "1", "B": "2"})
    out = to_deprecate_dotenv(env)
    assert "A=1" in out
    assert "B=2" in out
