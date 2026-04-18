"""Tests for envpatch.profile."""
import pytest
from pathlib import Path
from envpatch.profile import profile_path, list_profiles, load_profile, merged_profile
from envpatch.parser import EnvFile


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content)
    return p


def test_profile_path_format():
    assert str(profile_path(".env", "staging")) == ".env.staging"
    assert str(profile_path(".env", "production")) == ".env.production"


def test_list_profiles_empty(tmp_path):
    write(tmp_path, ".env", "KEY=val\n")
    profiles = list_profiles(base=".env", directory=str(tmp_path))
    assert profiles == []


def test_list_profiles_finds_profiles(tmp_path):
    write(tmp_path, ".env", "KEY=val\n")
    write(tmp_path, ".env.staging", "KEY=stg\n")
    write(tmp_path, ".env.production", "KEY=prod\n")
    profiles = list_profiles(base=".env", directory=str(tmp_path))
    assert profiles == ["production", "staging"]


def test_load_profile_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_profile("staging", base=".env", directory=str(tmp_path))


def test_load_profile_returns_env_file(tmp_path):
    write(tmp_path, ".env.staging", "DB_HOST=stg-db\nDEBUG=true\n")
    env = load_profile("staging", base=".env", directory=str(tmp_path))
    assert env.get("DB_HOST") == "stg-db"
    assert env.get("DEBUG") == "true"


def test_merged_profile_overrides_base(tmp_path):
    write(tmp_path, ".env", "DB_HOST=localhost\nSECRET=base_secret\n")
    write(tmp_path, ".env.staging", "DB_HOST=stg-db\n")
    merged = merged_profile("staging", base=".env", directory=str(tmp_path))
    assert merged.get("DB_HOST") == "stg-db"
    assert merged.get("SECRET") == "base_secret"


def test_merged_profile_no_base(tmp_path):
    write(tmp_path, ".env.staging", "ONLY_KEY=value\n")
    merged = merged_profile("staging", base=".env", directory=str(tmp_path))
    assert merged.get("ONLY_KEY") == "value"
