"""Build a searchable index of keys across multiple .env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envpatch.parser import EnvFile


@dataclass
class IndexEntry:
    key: str
    value: str
    source: str  # file path as string

    def __str__(self) -> str:
        return f"{self.source}: {self.key}={self.value}"


@dataclass
class IndexResult:
    entries: List[IndexEntry] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.entries) == 0

    def sources(self) -> List[str]:
        return sorted({e.source for e in self.entries})

    def keys(self) -> List[str]:
        return sorted({e.key for e in self.entries})

    def find_key(self, key: str) -> List[IndexEntry]:
        return [e for e in self.entries if e.key == key]

    def find_in_source(self, source: str) -> List[IndexEntry]:
        return [e for e in self.entries if e.source == source]

    def duplicates(self) -> Dict[str, List[IndexEntry]]:
        """Return keys that appear in more than one source file."""
        from collections import defaultdict
        grouped: Dict[str, List[IndexEntry]] = defaultdict(list)
        for entry in self.entries:
            grouped[entry.key].append(entry)
        return {k: v for k, v in grouped.items() if len(v) > 1}


def build_index(paths: List[str], base_dir: Optional[str] = None) -> IndexResult:
    """Parse each file and collect all key/value entries into a unified index."""
    result = IndexResult()
    for raw_path in paths:
        p = Path(raw_path)
        if base_dir:
            p = Path(base_dir) / p
        if not p.exists():
            raise FileNotFoundError(f"env file not found: {p}")
        env = EnvFile.parse(p.read_text())
        source = str(p)
        for key in env.keys():
            value = env.get(key) or ""
            result.entries.append(IndexEntry(key=key, value=value, source=source))
    return result
