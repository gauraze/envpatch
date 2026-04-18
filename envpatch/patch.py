"""Apply diffs to env files, producing patched output."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .diff import DiffEntry, ChangeType
from .parser import EnvFile


def apply_patch(
    target: EnvFile,
    changes: List[DiffEntry],
    *,
    dry_run: bool = False,
) -> EnvFile:
    """Return a new EnvFile with the given changes applied.

    Args:
        target: The env file to patch.
        changes: List of DiffEntry objects describing what to change.
        dry_run: If True, return the patched file without writing to disk.

    Returns:
        A new EnvFile reflecting the applied changes.
    """
    lines: list[str] = list(target.raw_lines)
    # Build index: key -> line number
    key_to_line: dict[str, int] = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            key_to_line[key] = i

    for entry in changes:
        if entry.change_type == ChangeType.ADDED:
            lines.append(f"{entry.key}={entry.new_value}\n")
        elif entry.change_type == ChangeType.REMOVED:
            idx = key_to_line.get(entry.key)
            if idx is not None:
                lines[idx] = ""
        elif entry.change_type == ChangeType.MODIFIED:
            idx = key_to_line.get(entry.key)
            if idx is not None:
                lines[idx] = f"{entry.key}={entry.new_value}\n"
            else:
                lines.append(f"{entry.key}={entry.new_value}\n")

    patched_content = "".join(lines)
    patched = EnvFile.from_string(patched_content, path=target.path)

    if not dry_run and target.path:
        Path(target.path).write_text(patched_content)

    return patched
