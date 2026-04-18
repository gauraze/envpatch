"""Profile support: load environment-specific .env files (e.g. .env.staging)."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from envpatch.parser import EnvFile

DEFAULT_BASE = ".env"


def profile_path(base: str, profile: str) -> Path:
    """Return the path for a given profile, e.g. .env + staging -> .env.staging."""
    return Path(f"{base}.{profile}")


def list_profiles(base: str = DEFAULT_BASE, directory: str = ".") -> List[str]:
    """Discover available profiles by scanning directory for .env.<profile> files."""
    base_name = Path(base).name
    profiles: List[str] = []
    for p in Path(directory).iterdir():
        if p.name.startswith(base_name + ".") and p.is_file():
            suffix = p.name[len(base_name) + 1:]
            if suffix:
                profiles.append(suffix)
    return sorted(profiles)


def load_profile(
    profile: str,
    base: str = DEFAULT_BASE,
    directory: str = ".",
) -> EnvFile:
    """Load an EnvFile for the given profile."""
    path = Path(directory) / profile_path(base, profile)
    if not path.exists():
        raise FileNotFoundError(f"Profile file not found: {path}")
    return EnvFile.parse(path.read_text())


def merged_profile(
    profile: str,
    base: str = DEFAULT_BASE,
    directory: str = ".",
) -> EnvFile:
    """Return base .env merged with profile overrides (profile wins on conflict)."""
    from envpatch.merge import merge_env_files, MergeStrategy

    base_path = Path(directory) / base
    base_env = EnvFile.parse(base_path.read_text()) if base_path.exists() else EnvFile([])
    profile_env = load_profile(profile, base, directory)
    return merge_env_files(base_env, profile_env, strategy=MergeStrategy.THEIRS)
