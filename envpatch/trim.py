from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class TrimResult:
    entries: List[EnvEntry]
    removed: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.removed) == 0


def trim_env(
    env: EnvFile,
    *,
    keys: Optional[List[str]] = None,
    prefixes: Optional[List[str]] = None,
    empty_only: bool = False,
) -> TrimResult:
    """Remove keys from env, optionally restricted to specific keys/prefixes."""
    kept: List[EnvEntry] = []
    removed: List[str] = []

    for entry in env.entries:
        should_remove = False

        if keys and entry.key in keys:
            should_remove = True
        elif prefixes and any(entry.key.startswith(p) for p in prefixes):
            should_remove = True

        if should_remove and empty_only and entry.value != "":
            should_remove = False

        if should_remove:
            removed.append(entry.key)
        else:
            kept.append(entry)

    return TrimResult(entries=kept, removed=removed)


def to_trimmed_dotenv(result: TrimResult) -> str:
    lines = []
    for e in result.entries:
        if e.comment and not e.key:
            lines.append(e.comment)
        else:
            lines.append(f"{e.key}={e.value}")
    return "\n".join(lines)
