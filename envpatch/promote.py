"""Promote .env values from one environment profile to another."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile
from envpatch.diff import diff_env_files, ChangeType
from envpatch.profile import load_profile, profile_path


@dataclass
class PromoteResult:
    source: str
    target: str
    promoted: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.conflicts) == 0


def promote_keys(
    source: EnvFile,
    target: EnvFile,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> tuple[EnvFile, PromoteResult]:
    """Promote keys from source into target, returning updated EnvFile and result."""
    result_data = dict(target.data)
    promoted, skipped, conflicts = [], [], []

    candidates = keys if keys else list(source.data.keys())

    for key in candidates:
        if key not in source.data:
            skipped.append(key)
            continue
        value = source.data[key]
        if key in result_data and result_data[key] != value:
            if overwrite:
                result_data[key] = value
                promoted.append(key)
                conflicts.append(key)
            else:
                conflicts.append(key)
                skipped.append(key)
        else:
            result_data[key] = value
            promoted.append(key)

    new_env = EnvFile(data=result_data, comments=target.comments)
    res = PromoteResult(
        source=getattr(source, 'name', 'source'),
        target=getattr(target, 'name', 'target'),
        promoted=promoted,
        skipped=skipped,
        conflicts=conflicts,
    )
    return new_env, res


def promote_profiles(
    source_name: str,
    target_name: str,
    base_dir: str = ".",
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> tuple[EnvFile, PromoteResult]:
    source = load_profile(source_name, base_dir)
    target = load_profile(target_name, base_dir)
    return promote_keys(source, target, keys=keys, overwrite=overwrite)
