"""Squash multiple .env files into a single merged result, with conflict resolution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile, EnvEntry


@dataclass
class SquashResult:
    entries: List[EnvEntry]
    conflicts: Dict[str, List[str]]  # key -> list of conflicting values
    sources: Dict[str, str]          # key -> filename that won
    clean: bool = field(init=False)

    def __post_init__(self) -> None:
        self.clean = len(self.conflicts) == 0

    def to_dotenv(self) -> str:
        lines = []
        for entry in self.entries:
            lines.append(f"{entry.key}={entry.value}")
        return "\n".join(lines) + ("\n" if lines else "")


def squash_envs(
    files: List[EnvFile],
    filenames: Optional[List[str]] = None,
    last_wins: bool = True,
) -> SquashResult:
    """Squash a list of EnvFile objects into one.

    Args:
        files: Ordered list of EnvFile objects to merge.
        filenames: Optional display names aligned with *files*.
        last_wins: When True the last file's value wins on conflict;
                   when False the first file's value wins.
    """
    if filenames is None:
        filenames = [f"file{i}" for i in range(len(files))]

    if len(filenames) != len(files):
        raise ValueError("filenames length must match files length")

    seen: Dict[str, EnvEntry] = {}
    winner: Dict[str, str] = {}
    conflicts: Dict[str, List[str]] = {}

    for env_file, fname in zip(files, filenames):
        for key in env_file.keys():
            entry = env_file.get(key)
            if entry is None:
                continue
            if key not in seen:
                seen[key] = entry
                winner[key] = fname
            else:
                existing_val = seen[key].value
                if existing_val != entry.value:
                    if key not in conflicts:
                        conflicts[key] = [existing_val]
                    conflicts[key].append(entry.value)
                    if last_wins:
                        seen[key] = entry
                        winner[key] = fname

    entries = list(seen.values())
    return SquashResult(entries=entries, conflicts=conflicts, sources=winner)
