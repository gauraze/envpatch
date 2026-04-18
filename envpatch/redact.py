"""Redact sensitive values in .env files based on key patterns."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

from envpatch.parser import EnvFile

DEFAULT_PATTERNS: List[str] = [
    r".*SECRET.*",
    r".*PASSWORD.*",
    r".*TOKEN.*",
    r".*API_KEY.*",
    r".*PRIVATE.*",
    r".*CREDENTIAL.*",
]

DEFAULT_PLACEHOLDER = "***REDACTED***"


@dataclass
class RedactResult:
    original: EnvFile
    redacted: dict  # key -> value (possibly redacted)
    redacted_keys: List[str] = field(default_factory=list)

    def to_dotenv(self) -> str:
        lines = []
        for key, value in self.redacted.items():
            lines.append(f"{key}={value}")
        return "\n".join(lines)


def _matches_any(key: str, patterns: List[str]) -> bool:
    upper = key.upper()
    return any(re.fullmatch(p, upper) for p in patterns)


def redact(
    env: EnvFile,
    patterns: List[str] | None = None,
    placeholder: str = DEFAULT_PLACEHOLDER,
) -> RedactResult:
    """Return a RedactResult with sensitive values replaced by placeholder."""
    if patterns is None:
        patterns = DEFAULT_PATTERNS

    redacted: dict = {}
    redacted_keys: List[str] = []

    for entry in env.entries:
        if entry.comment or entry.key is None:
            continue
        if _matches_any(entry.key, patterns):
            redacted[entry.key] = placeholder
            redacted_keys.append(entry.key)
        else:
            redacted[entry.key] = entry.value

    return RedactResult(original=env, redacted=redacted, redacted_keys=redacted_keys)
