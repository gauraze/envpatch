"""Generate stub .env files from a list of keys with empty or placeholder values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class StubResult:
    entries: list[EnvEntry]
    generated: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.generated) == 0


def stub_env(
    keys: list[str],
    placeholder: str = "",
    existing: Optional[EnvFile] = None,
    overwrite: bool = False,
) -> StubResult:
    """Create stub entries for the given keys.

    If *existing* is provided, keys already present are skipped unless
    *overwrite* is True.
    """
    result_entries: list[EnvEntry] = []
    generated: list[str] = []

    existing_keys: set[str] = set()
    if existing is not None:
        existing_keys = set(existing.keys())
        # Carry over existing entries first
        for entry in existing._entries:  # type: ignore[attr-defined]
            result_entries.append(entry)

    for key in keys:
        if key in existing_keys and not overwrite:
            continue
        if key in existing_keys and overwrite:
            # Replace in-place
            result_entries = [
                EnvEntry(key=key, value=placeholder, comment=None)
                if e.key == key else e
                for e in result_entries
            ]
        else:
            result_entries.append(EnvEntry(key=key, value=placeholder, comment=None))
        generated.append(key)

    return StubResult(entries=result_entries, generated=generated)


def to_stub_dotenv(result: StubResult) -> str:
    lines: list[str] = []
    for entry in result.entries:
        if entry.comment:
            lines.append(f"# {entry.comment}")
        lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines) + ("\n" if lines else "")
