"""Compare two env profiles or snapshots side-by-side."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile
from envpatch.diff import DiffEntry, diff_env_files, ChangeType


@dataclass
class CompareResult:
    base_name: str
    other_name: str
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def added(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.change == ChangeType.ADDED]

    @property
    def removed(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.change == ChangeType.REMOVED]

    @property
    def modified(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.change == ChangeType.MODIFIED]

    @property
    def unchanged(self) -> List[DiffEntry]:
        return [e for e in self.entries if e.change == ChangeType.UNCHANGED]

    @property
    def is_identical(self) -> bool:
        return len(self.added) == 0 and len(self.removed) == 0 and len(self.modified) == 0


def compare_envs(
    base: EnvFile,
    other: EnvFile,
    base_name: str = "base",
    other_name: str = "other",
    include_unchanged: bool = False,
) -> CompareResult:
    entries = diff_env_files(base, other, include_unchanged=include_unchanged)
    return CompareResult(base_name=base_name, other_name=other_name, entries=entries)


def compare_summary(result: CompareResult) -> Dict[str, int]:
    return {
        "added": len(result.added),
        "removed": len(result.removed),
        "modified": len(result.modified),
        "unchanged": len(result.unchanged),
    }
