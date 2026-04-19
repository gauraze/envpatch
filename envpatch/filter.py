from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class FilterResult:
    matched: List[EnvEntry] = field(default_factory=list)
    excluded: List[EnvEntry] = field(default_factory=list)

    @property
    def clean(self) -> EnvFile:
        from envpatch.parser import EnvFile
        ef = EnvFile(entries=list(self.matched))
        return ef


def filter_keys(
    env: EnvFile,
    *,
    prefixes: Optional[List[str]] = None,
    suffixes: Optional[List[str]] = None,
    contains: Optional[str] = None,
    keys: Optional[List[str]] = None,
    invert: bool = False,
) -> FilterResult:
    """Return entries matching any of the given criteria."""
    matched: List[EnvEntry] = []
    excluded: List[EnvEntry] = []

    for entry in env.entries:
        k = entry.key
        hit = False
        if keys and k in keys:
            hit = True
        if prefixes and any(k.startswith(p) for p in prefixes):
            hit = True
        if suffixes and any(k.endswith(s) for s in suffixes):
            hit = True
        if contains and contains in k:
            hit = True
        if invert:
            hit = not hit
        (matched if hit else excluded).append(entry)

    return FilterResult(matched=matched, excluded=excluded)


def to_filtered_dotenv(result: FilterResult) -> str:
    lines = []
    for entry in result.matched:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        lines.append(f"{entry.key}={entry.raw_value}")
    return "\n".join(lines) + ("\n" if lines else "")
