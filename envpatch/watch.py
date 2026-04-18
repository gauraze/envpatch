"""Watch a .env file for changes and emit diffs."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from envpatch.parser import EnvFile
from envpatch.diff import DiffEntry, diff_env_files


@dataclass
class WatchEvent:
    path: Path
    changes: list[DiffEntry]
    timestamp: float = field(default_factory=time.time)

    def has_changes(self) -> bool:
        return len(self.changes) > 0


def watch_env_file(
    path: Path,
    callback: Callable[[WatchEvent], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *path* every *interval* seconds; call *callback* when changes detected."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    previous = EnvFile.parse(path.read_text())
    iterations = 0

    while True:
        if max_iterations is not None and iterations >= max_iterations:
            break
        time.sleep(interval)
        iterations += 1
        try:
            current_text = path.read_text()
        except FileNotFoundError:
            break
        current = EnvFile.parse(current_text)
        changes = [e for e in diff_env_files(previous, current) if e.change_type.name != "UNCHANGED"]
        if changes:
            callback(WatchEvent(path=path, changes=changes))
        previous = current
