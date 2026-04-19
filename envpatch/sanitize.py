from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry

_CONTROL_CHARS = set(range(0, 32)) - {9, 10, 13}  # allow tab, LF, CR


@dataclass
class SanitizeIssue:
    key: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason}"


@dataclass
class SanitizeResult:
    entries: List[EnvEntry]
    issues: List[SanitizeIssue] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.issues) == 0

    def to_dotenv(self) -> str:
        lines = []
        for e in self.entries:
            lines.append(f"{e.key}={e.value}")
        return "\n".join(lines) + ("\n" if lines else "")


def _has_control_chars(value: str) -> bool:
    return any(ord(c) in _CONTROL_CHARS for c in value)


def _strip_control_chars(value: str) -> str:
    return "".join(c for c in value if ord(c) not in _CONTROL_CHARS)


def sanitize_env(
    env: EnvFile,
    strip_control: bool = True,
    strip_whitespace: bool = True,
    remove_empty: bool = False,
    allowed_keys: Optional[List[str]] = None,
) -> SanitizeResult:
    entries: List[EnvEntry] = []
    issues: List[SanitizeIssue] = []

    for entry in env.entries:
        value = entry.value

        if allowed_keys is not None and entry.key not in allowed_keys:
            issues.append(SanitizeIssue(entry.key, "key not in allowed list, skipped"))
            continue

        if _has_control_chars(value):
            issues.append(SanitizeIssue(entry.key, "contained control characters, stripped"))
            if strip_control:
                value = _strip_control_chars(value)

        if strip_whitespace:
            stripped = value.strip()
            if stripped != value:
                issues.append(SanitizeIssue(entry.key, "leading/trailing whitespace removed"))
                value = stripped

        if remove_empty and value == "":
            issues.append(SanitizeIssue(entry.key, "empty value, key removed"))
            continue

        entries.append(EnvEntry(key=entry.key, value=value, comment=entry.comment))

    return SanitizeResult(entries=entries, issues=issues)
