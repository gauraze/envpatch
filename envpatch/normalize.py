from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class NormalizeIssue:
    key: str
    original: str
    normalized: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason} ({self.original!r} -> {self.normalized!r})"


@dataclass
class NormalizeResult:
    entries: List[EnvEntry]
    issues: List[NormalizeIssue] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.issues) == 0

    def to_dotenv(self) -> str:
        lines = []
        for e in self.entries:
            if e.comment:
                lines.append(e.raw)
            else:
                lines.append(f"{e.key}={e.value}")
        return "\n".join(lines) + "\n" if lines else ""


def normalize_env(
    env: EnvFile,
    *,
    uppercase_keys: bool = True,
    strip_quotes: bool = True,
    strip_whitespace: bool = True,
    keys: Optional[List[str]] = None,
) -> NormalizeResult:
    issues: List[NormalizeIssue] = []
    entries: List[EnvEntry] = []

    for entry in env.entries:
        if entry.comment or entry.key is None:
            entries.append(entry)
            continue

        target = keys is None or entry.key in keys
        new_key = entry.key
        new_val = entry.value

        if target and uppercase_keys and entry.key != entry.key.upper():
            new_key = entry.key.upper()
            issues.append(NormalizeIssue(entry.key, entry.key, new_key, "key uppercased"))

        if target and strip_whitespace and new_val != new_val.strip():
            stripped = new_val.strip()
            issues.append(NormalizeIssue(new_key, new_val, stripped, "value whitespace stripped"))
            new_val = stripped

        if target and strip_quotes:
            for q in ('"', "'"):
                if new_val.startswith(q) and new_val.endswith(q) and len(new_val) >= 2:
                    unquoted = new_val[1:-1]
                    issues.append(NormalizeIssue(new_key, new_val, unquoted, "quotes removed"))
                    new_val = unquoted
                    break

        entries.append(EnvEntry(key=new_key, value=new_val, raw=f"{new_key}={new_val}", comment=False))

    return NormalizeResult(entries=entries, issues=issues)
