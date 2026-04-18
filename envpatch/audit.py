"""Audit log for tracking changes applied to .env files."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional

AUDIT_VERSION = 1


@dataclass
class AuditEntry:
    timestamp: str
    action: str          # "patch" | "merge" | "snapshot"
    source: Optional[str]
    target: str
    keys_changed: List[str]
    note: Optional[str] = None


@dataclass
class AuditLog:
    version: int = AUDIT_VERSION
    entries: List[AuditEntry] = field(default_factory=list)

    def add(self, action: str, target: str, keys_changed: List[str],
            source: Optional[str] = None, note: Optional[str] = None) -> AuditEntry:
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            source=source,
            target=target,
            keys_changed=keys_changed,
            note=note,
        )
        self.entries.append(entry)
        return entry


def save_audit(log: AuditLog, path: str) -> None:
    data = {
        "version": log.version,
        "entries": [asdict(e) for e in log.entries],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_audit(path: str) -> AuditLog:
    if not os.path.exists(path):
        return AuditLog()
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if data.get("version") != AUDIT_VERSION:
        raise ValueError(f"Unsupported audit log version: {data.get('version')}")
    entries = [AuditEntry(**e) for e in data.get("entries", [])]
    return AuditLog(version=data["version"], entries=entries)


def append_audit(path: str, action: str, target: str, keys_changed: List[str],
                 source: Optional[str] = None, note: Optional[str] = None) -> AuditEntry:
    log = load_audit(path)
    entry = log.add(action=action, target=target, keys_changed=keys_changed,
                    source=source, note=note)
    save_audit(log, path)
    return entry
