"""Resolve missing keys in an env file from one or more fallback env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envpatch.parser import EnvFile, EnvEntry


@dataclass
class ResolveResult:
    resolved: List[EnvEntry] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)
    entries: List[EnvEntry] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.unresolved) == 0

    def to_dotenv(self) -> str:
        lines = []
        for entry in self.entries:
            lines.append(f"{entry.key}={entry.value}")
        return "\n".join(lines)


def resolve_env(
    base: EnvFile,
    fallbacks: List[EnvFile],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> ResolveResult:
    """Fill missing (or empty) keys in *base* from the first fallback that has them.

    Args:
        base:      The primary EnvFile to resolve into.
        fallbacks: Ordered list of fallback EnvFiles to source values from.
        keys:      Optional explicit list of keys to resolve. Defaults to all keys
                   in base that are empty, plus keys present in any fallback but
                   absent from base.
        overwrite: If True, overwrite non-empty base values with fallback values.
    """
    # Build a mutable dict from base
    merged: dict[str, str] = {e.key: e.value for e in base.entries}

    # Collect all candidate keys
    if keys is not None:
        candidate_keys = list(keys)
    else:
        candidate_keys = list(merged.keys())
        for fb in fallbacks:
            for entry in fb.entries:
                if entry.key not in candidate_keys:
                    candidate_keys.append(entry.key)

    resolved_entries: List[EnvEntry] = []
    unresolved: List[str] = []

    for key in candidate_keys:
        base_value = merged.get(key, None)
        needs_resolve = base_value is None or base_value == "" or overwrite

        if not needs_resolve:
            continue

        found = False
        for fb in fallbacks:
            fb_value = fb.get(key)
            if fb_value is not None and fb_value != "":
                merged[key] = fb_value
                resolved_entries.append(EnvEntry(key=key, value=fb_value))
                found = True
                break

        if not found and (base_value is None or base_value == ""):
            unresolved.append(key)

    # Rebuild ordered entries from original base, then append new keys
    base_keys = {e.key for e in base.entries}
    final_entries: List[EnvEntry] = []
    for entry in base.entries:
        final_entries.append(EnvEntry(key=entry.key, value=merged.get(entry.key, entry.value)))
    for key in candidate_keys:
        if key not in base_keys:
            if key in merged:
                final_entries.append(EnvEntry(key=key, value=merged[key]))

    return ResolveResult(
        resolved=resolved_entries,
        unresolved=unresolved,
        entries=final_entries,
    )
