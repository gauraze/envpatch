from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class SortResult:
    original: List[EnvEntry]
    sorted_entries: List[EnvEntry]

    @property
    def changed(self) -> bool:
        orig_keys = [e.key for e in self.original]
        sort_keys = [e.key for e in self.sorted_entries]
        return orig_keys != sort_keys


def sort_env(
    env: EnvFile,
    reverse: bool = False,
    group_prefix: bool = False,
) -> SortResult:
    """Return a SortResult with entries sorted alphabetically.

    Args:
        env: The parsed EnvFile to sort.
        reverse: If True, sort in descending order.
        group_prefix: If True, group keys by their prefix (part before first '_').
    """
    entries = list(env.entries)

    if group_prefix:
        def _prefix(e: EnvEntry) -> tuple:
            prefix = e.key.split("_")[0] if "_" in e.key else e.key
            return (prefix, e.key)
        sorted_entries = sorted(entries, key=_prefix, reverse=reverse)
    else:
        sorted_entries = sorted(entries, key=lambda e: e.key, reverse=reverse)

    return SortResult(original=entries, sorted_entries=sorted_entries)


def to_sorted_dotenv(result: SortResult) -> str:
    """Serialize sorted entries back to .env format."""
    lines = []
    for entry in result.sorted_entries:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        if entry.value is None:
            lines.append(entry.key)
        else:
            lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines) + ("\n" if lines else "")
