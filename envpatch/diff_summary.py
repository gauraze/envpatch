from dataclasses import dataclass, field
from typing import List
from envpatch.diff import DiffEntry, ChangeType


@dataclass
class DiffSummary:
    added: int = 0
    removed: int = 0
    modified: int = 0
    unchanged: int = 0
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return self.added + self.removed + self.modified

    @property
    def clean(self) -> bool:
        return self.total_changes == 0

    def __str__(self) -> str:
        lines = [f"Summary: +{self.added} -{self.removed} ~{self.modified}"]
        if self.unchanged:
            lines.append(f"  ({self.unchanged} unchanged)")
        return "\n".join(lines)


def summarize(entries: List[DiffEntry]) -> DiffSummary:
    summary = DiffSummary(entries=entries)
    for e in entries:
        if e.change == ChangeType.ADDED:
            summary.added += 1
        elif e.change == ChangeType.REMOVED:
            summary.removed += 1
        elif e.change == ChangeType.MODIFIED:
            summary.modified += 1
        else:
            summary.unchanged += 1
    return summary


def format_summary_table(summary: DiffSummary, show_unchanged: bool = False) -> str:
    lines = []
    for e in summary.entries:
        if e.change == ChangeType.UNCHANGED and not show_unchanged:
            continue
        symbol = {ChangeType.ADDED: "+", ChangeType.REMOVED: "-",
                  ChangeType.MODIFIED: "~", ChangeType.UNCHANGED: " "}.get(e.change, "?")
        old = e.old_value or ""
        new = e.new_value or ""
        if e.change == ChangeType.MODIFIED:
            lines.append(f"  {symbol} {e.key}: {old!r} -> {new!r}")
        elif e.change == ChangeType.ADDED:
            lines.append(f"  {symbol} {e.key}={new!r}")
        elif e.change == ChangeType.REMOVED:
            lines.append(f"  {symbol} {e.key} (was {old!r})")
        else:
            lines.append(f"  {symbol} {e.key}={new!r}")
    header = str(summary)
    return header + ("\n" + "\n".join(lines) if lines else "")
