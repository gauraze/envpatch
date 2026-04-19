from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry

DEFAULT_PATTERNS = ["SECRET", "PASSWORD", "TOKEN", "KEY", "PRIVATE", "AUTH", "CREDENTIAL"]
DEFAULT_MASK = "***"


@dataclass
class MaskResult:
    entries: List[EnvEntry]
    masked_keys: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.masked_keys) == 0

    def to_dotenv(self) -> str:
        lines = []
        for e in self.entries:
            if e.comment is not None:
                lines.append(e.comment)
            else:
                lines.append(f"{e.key}={e.value}")
        return "\n".join(lines)


def _matches(key: str, patterns: List[str]) -> bool:
    upper = key.upper()
    return any(p in upper for p in patterns)


def mask_env(
    env: EnvFile,
    patterns: Optional[List[str]] = None,
    placeholder: str = DEFAULT_MASK,
    keys: Optional[List[str]] = None,
) -> MaskResult:
    active_patterns = patterns if patterns is not None else DEFAULT_PATTERNS
    masked_keys: List[str] = []
    result: List[EnvEntry] = []

    for entry in env.entries:
        if entry.key is None:
            result.append(entry)
            continue
        should_mask = (keys and entry.key in keys) or (
            not keys and _matches(entry.key, active_patterns)
        )
        if should_mask:
            masked_keys.append(entry.key)
            result.append(EnvEntry(key=entry.key, value=placeholder, comment=None, raw=entry.raw))
        else:
            result.append(entry)

    return MaskResult(entries=result, masked_keys=masked_keys)
