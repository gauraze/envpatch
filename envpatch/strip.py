from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile


@dataclass
class StripResult:
    removed: List[str] = field(default_factory=list)
    kept: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.removed) == 0


def strip_keys(
    env: EnvFile,
    keys: List[str],
    *,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
) -> tuple[EnvFile, StripResult]:
    """Remove keys from env by exact name, prefix, or suffix match."""
    result = StripResult()
    new_entries = []

    for entry in env.entries:
        matched = False
        if entry.key in keys:
            matched = True
        elif prefix and entry.key.startswith(prefix):
            matched = True
        elif suffix and entry.key.endswith(suffix):
            matched = True

        if matched:
            result.removed.append(entry.key)
        else:
            result.kept.append(entry.key)
            new_entries.append(entry)

    new_env = EnvFile(entries=new_entries)
    return new_env, result


def to_stripped_dotenv(env: EnvFile) -> str:
    lines = []
    for entry in env.entries:
        if entry.comment:
            lines.append(entry.comment)
        lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines) + ("\n" if lines else "")
