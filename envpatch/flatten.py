from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class FlattenResult:
    entries: List[EnvEntry]
    merged_from: List[str]
    conflicts: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return len(self.conflicts) == 0


def flatten_envs(
    files: List[EnvFile],
    labels: Optional[List[str]] = None,
    overwrite: bool = True,
) -> FlattenResult:
    """Merge multiple EnvFiles into a single flat list of entries.

    Later files take precedence when overwrite=True (default).
    Conflicts are recorded when the same key appears with different values.
    """
    if labels is None:
        labels = [f"file{i}" for i in range(len(files))]

    seen: Dict[str, str] = {}
    origin: Dict[str, str] = {}
    conflicts: Dict[str, List[str]] = {}
    order: List[str] = []

    for label, env in zip(labels, files):
        for key in env.keys():
            value = env.get(key) or ""
            if key not in seen:
                seen[key] = value
                origin[key] = label
                order.append(key)
            else:
                if seen[key] != value:
                    if key not in conflicts:
                        conflicts[key] = [f"{origin[key]}={seen[key]}"]
                    conflicts[key].append(f"{label}={value}")
                if overwrite:
                    seen[key] = value
                    origin[key] = label

    entries = [EnvEntry(key=k, value=seen[k], comment=None, raw=f"{k}={seen[k]}") for k in order]
    return FlattenResult(entries=entries, merged_from=labels, conflicts=conflicts)


def to_flattened_dotenv(result: FlattenResult) -> str:
    return "\n".join(f"{e.key}={e.value}" for e in result.entries) + "\n"
