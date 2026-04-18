"""Parser for .env files."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class EnvEntry:
    key: str
    value: str
    comment: Optional[str] = None
    line_number: int = 0


@dataclass
class EnvFile:
    path: Path
    entries: Dict[str, EnvEntry] = field(default_factory=dict)
    raw_lines: List[str] = field(default_factory=list)

    def keys(self):
        return self.entries.keys()

    def get(self, key: str) -> Optional[EnvEntry]:
        return self.entries.get(key)


COMMENT_RE = re.compile(r"^\s*#")
EMPTY_RE = re.compile(r"^\s*$")
ENTRY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def _strip_quotes(value: str) -> str:
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            return value[1:-1]
    return value


def parse_env_file(path: Path) -> EnvFile:
    """Parse a .env file and return an EnvFile instance."""
    env_file = EnvFile(path=path)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    pending_comment: Optional[str] = None
    with path.open("r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            env_file.raw_lines.append(line)
            stripped = line.rstrip("\n")
            if COMMENT_RE.match(stripped):
                pending_comment = stripped.lstrip("# ").strip()
                continue
            if EMPTY_RE.match(stripped):
                pending_comment = None
                continue
            m = ENTRY_RE.match(stripped)
            if m:
                key, raw_value = m.group(1), m.group(2).strip()
                value = _strip_quotes(raw_value)
                entry = EnvEntry(
                    key=key,
                    value=value,
                    comment=pending_comment,
                    line_number=lineno,
                )
                env_file.entries[key] = entry
                pending_comment = None

    return env_file
