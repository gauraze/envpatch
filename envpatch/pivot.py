"""Pivot: transpose env key-value pairs into a column-oriented mapping.

Useful for comparing multiple env files side-by-side in a table format.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile


@dataclass
class PivotResult:
    """Column-oriented view of multiple env files."""
    labels: List[str]                          # file labels (e.g. dev, staging)
    rows: Dict[str, List[Optional[str]]]       # key -> [value_per_file]
    missing_marker: str = "<missing>"

    @property
    def clean(self) -> bool:
        """True when every key is present in every file."""
        return all(
            v is not None for values in self.rows.values() for v in values
        )

    def keys(self) -> List[str]:
        return sorted(self.rows.keys())

    def to_table(self) -> List[List[str]]:
        """Return a list of rows suitable for tabular rendering.

        First row is the header: ["KEY", *labels].
        Subsequent rows: [key, value_for_label_0, value_for_label_1, ...].
        """
        header = ["KEY"] + self.labels
        body = [
            [k] + [v if v is not None else self.missing_marker for v in self.rows[k]]
            for k in self.keys()
        ]
        return [header] + body


def pivot_envs(
    files: List[EnvFile],
    labels: Optional[List[str]] = None,
    missing_marker: str = "<missing>",
) -> PivotResult:
    """Pivot a list of EnvFile objects into a PivotResult.

    Args:
        files: Ordered list of parsed env files.
        labels: Human-readable label for each file.  Defaults to
                "file_0", "file_1", … when not provided.
        missing_marker: String used to represent absent keys in output.
    """
    if labels is None:
        labels = [f"file_{i}" for i in range(len(files))]

    if len(labels) != len(files):
        raise ValueError(
            f"labels length ({len(labels)}) must match files length ({len(files)})"
        )

    all_keys: List[str] = []
    seen: set = set()
    for ef in files:
        for k in ef.keys():
            if k not in seen:
                all_keys.append(k)
                seen.add(k)

    rows: Dict[str, List[Optional[str]]] = {}
    for k in all_keys:
        rows[k] = [ef.get(k) for ef in files]

    return PivotResult(labels=labels, rows=rows, missing_marker=missing_marker)
