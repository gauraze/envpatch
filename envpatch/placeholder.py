from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class PlaceholderIssue:
    key: str
    value: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason} (value={self.value!r})"


@dataclass
class PlaceholderResult:
    entries: List[EnvEntry]
    issues: List[PlaceholderIssue] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.issues) == 0

    def to_dotenv(self) -> str:
        return "\n".join(f"{e.key}={e.value}" for e in self.entries)


_DEFAULT_PATTERNS = ["{{", "}}", "<", ">", "CHANGEME", "TODO", "FIXME", "PLACEHOLDER", "REPLACE_ME"]


def _is_placeholder(value: str, patterns: List[str]) -> Optional[str]:
    v = value.strip()
    if not v:
        return None
    for p in patterns:
        if p in v:
            return f"looks like a placeholder (matched {p!r})"
    return None


def check_placeholders(
    env: EnvFile,
    patterns: Optional[List[str]] = None,
    keys: Optional[List[str]] = None,
) -> PlaceholderResult:
    active_patterns = patterns if patterns is not None else _DEFAULT_PATTERNS
    issues: List[PlaceholderIssue] = []
    for entry in env.entries:
        if keys and entry.key not in keys:
            continue
        reason = _is_placeholder(entry.value, active_patterns)
        if reason:
            issues.append(PlaceholderIssue(key=entry.key, value=entry.value, reason=reason))
    return PlaceholderResult(entries=env.entries, issues=issues)
