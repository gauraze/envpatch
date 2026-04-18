"""Integration tests: promote through profiles on disk."""
import os
import pytest
from envpatch.promote import promote_profiles


@pytest.fixture
def env_dir(tmp_path):
    (tmp_path / ".env.dev").write_text("API_URL=http://dev\nDEBUG=true\nSHARED=x\n")
    (tmp_path / ".env.staging").write_text("API_URL=http://staging\nSHARED=x\n")
    return tmp_path


def test_promote_new_keys_from_dev_to_staging(env_dir):
    updated, result = promote_profiles("dev", "staging", base_dir=str(env_dir))
    assert "DEBUG" in updated.data
    assert updated.data["DEBUG"] == "true"
    assert "DEBUG" in result.promoted


def test_promote_conflict_detected(env_dir):
    updated, result = promote_profiles("dev", "staging", base_dir=str(env_dir))
    assert "API_URL" in result.conflicts
    assert updated.data["API_URL"] == "http://staging"  # not overwritten


def test_promote_overwrite_resolves_conflict(env_dir):
    updated, result = promote_profiles(
        "dev", "staging", base_dir=str(env_dir), overwrite=True
    )
    assert updated.data["API_URL"] == "http://dev"
    assert result.clean is True  # conflicts exist but overwrite applied


def test_promote_specific_keys_only(env_dir):
    updated, result = promote_profiles(
        "dev", "staging", base_dir=str(env_dir), keys=["DEBUG"]
    )
    assert "DEBUG" in updated.data
    assert result.promoted == ["DEBUG"]
