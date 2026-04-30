"""envpatch.dedup_keys — detect and remove duplicate key definitions across multiple env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envpatch.parser import EnvFile


@dataclass
class CrossFileDupe:
    key: str
    occurrences: List[Tuple[str, str]]  # list of (source_label, value)

    def __str__(self) -> str:
        parts = ", ".join(f"{src}={val!r}" for src, val in self.occurrences)
        return f"{self.key}: [{parts}]"


@dataclass
class CrossDupeResult:
    duplicates: List[CrossFileDupe] = field(default_factory=list)
    merged: EnvFile = field(default_factory=EnvFile)

    @property
    def clean(self) -> bool:
        return len(self.duplicates) == 0


def find_cross_duplicates(
    envs: List[Tuple[str, EnvFile]],
) -> List[CrossFileDupe]:
    """Return keys that appear in more than one file."""
    seen: Dict[str, List[Tuple[str, str]]] = {}
    for label, env in envs:
        for key in env.keys():
            value = env.get(key) or ""
            seen.setdefault(key, []).append((label, value))
    return [
        CrossFileDupe(key=k, occurrences=v)
        for k, v in seen.items()
        if len(v) > 1
    ]


def dedup_cross(
    envs: List[Tuple[str, EnvFile]],
    keep: str = "last",
) -> CrossDupeResult:
    """Merge multiple env files, resolving cross-file duplicate keys.

    Args:
        envs:  Ordered list of (label, EnvFile) pairs.
        keep:  ``'last'`` (default) keeps the last definition;
               ``'first'`` keeps the first.
    """
    if keep not in ("first", "last"):
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")

    duplicates = find_cross_duplicates(envs)

    ordered = envs if keep == "last" else list(reversed(envs))
    merged = EnvFile()
    seen_keys: set = set()
    for _label, env in reversed(ordered) if keep == "last" else ordered:
        for key in env.keys():
            if key not in seen_keys:
                from envpatch.parser import EnvEntry
                entry = EnvEntry(key=key, value=env.get(key) or "", raw=f"{key}={env.get(key) or ''}")
                merged._entries.append(entry)  # type: ignore[attr-defined]
                seen_keys.add(key)

    return CrossDupeResult(duplicates=duplicates, merged=merged)
