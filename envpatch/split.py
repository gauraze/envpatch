from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class SplitResult:
    groups: Dict[str, List[EnvEntry]] = field(default_factory=dict)
    ungrouped: List[EnvEntry] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.ungrouped) == 0


def split_by_prefix(
    env: EnvFile,
    prefixes: List[str],
    sep: str = "_",
    keep_prefix: bool = True,
) -> SplitResult:
    groups: Dict[str, List[EnvEntry]] = {p: [] for p in prefixes}
    ungrouped: List[EnvEntry] = []

    for entry in env.entries:
        matched = False
        for prefix in prefixes:
            token = prefix + sep
            if entry.key.startswith(token):
                new_key = entry.key if keep_prefix else entry.key[len(token):]
                groups[prefix].append(EnvEntry(key=new_key, value=entry.value, comment=entry.comment))
                matched = True
                break
        if not matched:
            ungrouped.append(entry)

    return SplitResult(groups=groups, ungrouped=ungrouped)


def to_split_dotenv(entries: List[EnvEntry]) -> str:
    lines: List[str] = []
    for e in entries:
        if e.comment:
            lines.append(f"# {e.comment}")
        lines.append(f"{e.key}={e.value}")
    return "\n".join(lines) + ("\n" if lines else "")
