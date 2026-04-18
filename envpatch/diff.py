"""Diff logic for comparing two EnvFile instances."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from envpatch.parser import EnvFile


class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class DiffEntry:
    key: str
    change: ChangeType
    old_value: str | None = None
    new_value: str | None = None

    def __str__(self) -> str:
        if self.change == ChangeType.ADDED:
            return f"+ {self.key}={self.new_value}"
        if self.change == ChangeType.REMOVED:
            return f"- {self.key}={self.old_value}"
        if self.change == ChangeType.MODIFIED:
            return f"~ {self.key}: {self.old_value!r} -> {self.new_value!r}"
        return f"  {self.key}={self.old_value}"


def diff_env_files(
    base: EnvFile,
    target: EnvFile,
    include_unchanged: bool = False,
) -> List[DiffEntry]:
    """Compare base against target and return a list of DiffEntry objects."""
    results: List[DiffEntry] = []
    all_keys = sorted(set(base.keys()) | set(target.keys()))

    for key in all_keys:
        base_entry = base.get(key)
        target_entry = target.get(key)

        if base_entry is None:
            results.append(DiffEntry(key=key, change=ChangeType.ADDED, new_value=target_entry.value))
        elif target_entry is None:
            results.append(DiffEntry(key=key, change=ChangeType.REMOVED, old_value=base_entry.value))
        elif base_entry.value != target_entry.value:
            results.append(
                DiffEntry(
                    key=key,
                    change=ChangeType.MODIFIED,
                    old_value=base_entry.value,
                    new_value=target_entry.value,
                )
            )
        elif include_unchanged:
            results.append(DiffEntry(key=key, change=ChangeType.UNCHANGED, old_value=base_entry.value))

    return results
