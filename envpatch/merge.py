"""Merge two EnvFile objects with conflict resolution strategies."""

from enum import Enum
from typing import Dict, List, Optional
from envpatch.parser import EnvFile, EnvEntry


class MergeStrategy(str, Enum):
    OURS = "ours"       # prefer base on conflict
    THEIRS = "theirs"   # prefer other on conflict
    PROMPT = "prompt"   # raise on conflict (caller handles)


class MergeConflict(Exception):
    def __init__(self, key: str, base_val: str, other_val: str):
        self.key = key
        self.base_val = base_val
        self.other_val = other_val
        super().__init__(f"Conflict on key '{key}': '{base_val}' vs '{other_val}'")


def merge_env_files(
    base: EnvFile,
    other: EnvFile,
    strategy: MergeStrategy = MergeStrategy.THEIRS,
) -> EnvFile:
    """
    Merge `other` into `base`.

    - Keys only in `other` are added.
    - Keys only in `base` are kept.
    - Conflicting keys are resolved by `strategy`.
    """
    merged: Dict[str, EnvEntry] = {}

    base_keys = set(base.keys())
    other_keys = set(other.keys())

    for key in base_keys | other_keys:
        in_base = key in base_keys
        in_other = key in other_keys

        if in_base and not in_other:
            merged[key] = base.get(key)  # type: ignore[assignment]
        elif in_other and not in_base:
            merged[key] = other.get(key)  # type: ignore[assignment]
        else:
            base_entry = base.get(key)
            other_entry = other.get(key)
            if base_entry.value == other_entry.value:  # type: ignore[union-attr]
                merged[key] = base_entry  # type: ignore[assignment]
            elif strategy == MergeStrategy.OURS:
                merged[key] = base_entry  # type: ignore[assignment]
            elif strategy == MergeStrategy.THEIRS:
                merged[key] = other_entry  # type: ignore[assignment]
            else:
                raise MergeConflict(key, base_entry.value, other_entry.value)  # type: ignore[union-attr]

    # Preserve insertion order: base keys first, then new keys from other
    ordered: List[EnvEntry] = []
    seen = set()
    for key in list(base_keys) + [k for k in other_keys if k not in base_keys]:
        if key not in seen and key in merged:
            ordered.append(merged[key])
            seen.add(key)

    return EnvFile(entries=ordered)
