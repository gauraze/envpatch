"""Track and query change history for .env files."""
from __future__ import annotations
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

HISTORY_VERSION = 1


@dataclass
class HistoryEntry:
    timestamp: str
    source: str
    target: str
    changes: int
    summary: List[str] = field(default_factory=list)
    tag: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_entry(
    source: str,
    target: str,
    changes: int,
    summary: List[str],
    tag: Optional[str] = None,
) -> HistoryEntry:
    return HistoryEntry(
        timestamp=_now(),
        source=source,
        target=target,
        changes=changes,
        summary=summary,
        tag=tag,
    )


def save_history(entries: List[HistoryEntry], path: Path) -> None:
    path.write_text(
        json.dumps(
            {"version": HISTORY_VERSION, "entries": [asdict(e) for e in entries]},
            indent=2,
        )
    )


def load_history(path: Path) -> List[HistoryEntry]:
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    if data.get("version") != HISTORY_VERSION:
        raise ValueError(f"Unsupported history version: {data.get('version')}")
    return [HistoryEntry(**e) for e in data.get("entries", [])]


def append_history(entry: HistoryEntry, path: Path) -> None:
    entries = load_history(path)
    entries.append(entry)
    save_history(entries, path)


def filter_history(
    entries: List[HistoryEntry],
    source: Optional[str] = None,
    tag: Optional[str] = None,
) -> List[HistoryEntry]:
    result = entries
    if source:
        result = [e for e in result if e.source == source]
    if tag:
        result = [e for e in result if e.tag == tag]
    return result
