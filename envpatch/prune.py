from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class PruneResult:
    kept: list[EnvEntry]
    removed: list[EnvEntry]
    _clean: bool = field(init=False)

    def __post_init__(self) -> None:
        self._clean = len(self.removed) == 0

    @property
    def clean(self) -> bool:
        return self._clean


def prune_env(
    env: EnvFile,
    *,
    remove_empty: bool = True,
    remove_comments: bool = False,
    keys: Optional[list[str]] = None,
) -> PruneResult:
    """Remove unwanted entries from an EnvFile.

    Args:
        env: Source EnvFile to prune.
        remove_empty: Drop entries whose value is empty string.
        remove_comments: Drop comment-only lines.
        keys: Explicit list of keys to remove regardless of value.
    """
    kept: list[EnvEntry] = []
    removed: list[EnvEntry] = []
    explicit = set(keys or [])

    for entry in env.entries:
        if explicit and entry.key in explicit:
            removed.append(entry)
            continue
        if remove_empty and entry.key and entry.value == "":
            removed.append(entry)
            continue
        if remove_comments and not entry.key:
            removed.append(entry)
            continue
        kept.append(entry)

    return PruneResult(kept=kept, removed=removed)


def to_pruned_dotenv(result: PruneResult) -> str:
    lines = []
    for entry in result.kept:
        if entry.key:
            lines.append(f"{entry.key}={entry.value}")
        else:
            lines.append(entry.raw)
    return "\n".join(lines) + ("\n" if lines else "")
