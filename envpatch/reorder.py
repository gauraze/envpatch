from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class ReorderResult:
    entries: List[EnvEntry]
    moved: List[str] = field(default_factory=list)
    _clean: bool = True

    def clean(self) -> bool:
        return self._clean

    def to_dotenv(self) -> str:
        lines = []
        for e in self.entries:
            if e.comment is not None:
                lines.append(e.comment)
            lines.append(f"{e.key}={e.value}")
        return "\n".join(lines) + "\n" if lines else ""


def reorder_env(
    env: EnvFile,
    order: List[str],
    append_remaining: bool = True,
) -> ReorderResult:
    """Reorder keys in env according to the provided key list.

    Keys in *order* come first (in that order); remaining keys follow
    if *append_remaining* is True, otherwise they are dropped.
    """
    index = {e.key: e for e in env.entries}
    seen: set[str] = set()
    result: List[EnvEntry] = []
    moved: List[str] = []

    original_keys = [e.key for e in env.entries]

    for key in order:
        if key in index:
            result.append(index[key])
            seen.add(key)
            if original_keys.index(key) != len(result) - 1:
                moved.append(key)

    if append_remaining:
        for e in env.entries:
            if e.key not in seen:
                result.append(e)

    is_clean = result == env.entries
    return ReorderResult(entries=result, moved=moved, _clean=is_clean)
