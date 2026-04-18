"""Snapshot: save and load .env file snapshots for later comparison."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Optional

from envpatch.parser import EnvFile


SNAPSHOT_VERSION = 1


def save_snapshot(env: EnvFile, path: str, label: Optional[str] = None) -> dict:
    """Serialize an EnvFile to a JSON snapshot file."""
    data = {
        "version": SNAPSHOT_VERSION,
        "label": label or os.path.basename(path),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "entries": [
            {"key": e.key, "value": e.value, "comment": e.comment}
            for e in env.entries
        ],
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return data


def load_snapshot(path: str) -> EnvFile:
    """Deserialize a JSON snapshot file back into an EnvFile."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if data.get("version") != SNAPSHOT_VERSION:
        raise ValueError(
            f"Unsupported snapshot version: {data.get('version')}"
        )

    from envpatch.parser import EnvEntry

    entries = [
        EnvEntry(key=e["key"], value=e["value"], comment=e.get("comment"))
        for e in data["entries"]
    ]
    return EnvFile(entries=entries)


def snapshot_metadata(path: str) -> dict:
    """Return metadata from a snapshot without loading all entries."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {
        "version": data.get("version"),
        "label": data.get("label"),
        "created_at": data.get("created_at"),
        "entry_count": len(data.get("entries", [])),
    }
