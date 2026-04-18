"""Export diff results to various formats."""
from __future__ import annotations

import json
import csv
import io
from typing import List

from envpatch.diff import DiffEntry, ChangeType


def to_json(entries: List[DiffEntry], include_unchanged: bool = False) -> str:
    """Serialize diff entries to a JSON string."""
    records = []
    for entry in entries:
        if entry.change_type == ChangeType.UNCHANGED and not include_unchanged:
            continue
        records.append({
            "key": entry.key,
            "change": entry.change_type.value,
            "old_value": entry.old_value,
            "new_value": entry.new_value,
        })
    return json.dumps(records, indent=2)


def to_csv(entries: List[DiffEntry], include_unchanged: bool = False) -> str:
    """Serialize diff entries to a CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["key", "change", "old_value", "new_value"],
        lineterminator="\n",
    )
    writer.writeheader()
    for entry in entries:
        if entry.change_type == ChangeType.UNCHANGED and not include_unchanged:
            continue
        writer.writerow({
            "key": entry.key,
            "change": entry.change_type.value,
            "old_value": entry.old_value or "",
            "new_value": entry.new_value or "",
        })
    return output.getvalue()


def to_dotenv_patch(entries: List[DiffEntry]) -> str:
    """Produce a minimal .env snippet containing only changed/added keys."""
    lines = []
    for entry in entries:
        if entry.change_type in (ChangeType.ADDED, ChangeType.MODIFIED):
            lines.append(f"{entry.key}={entry.new_value or ''}")
        elif entry.change_type == ChangeType.REMOVED:
            lines.append(f"# REMOVED: {entry.key}")
    return "\n".join(lines)
