"""Apply default values to missing keys in an env file."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class DefaultsResult:
    entries: List[EnvEntry]
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.applied) == 0


def apply_defaults(
    env: EnvFile,
    defaults: Dict[str, str],
    overwrite: bool = False,
) -> DefaultsResult:
    """Merge defaults into env. Existing keys are kept unless overwrite=True."""
    entries = list(env.entries)
    existing_keys = {e.key for e in entries if e.key is not None}
    applied: List[str] = []
    skipped: List[str] = []

    for key, value in defaults.items():
        if key in existing_keys:
            if overwrite:
                entries = [
                    EnvEntry(key=key, value=value, comment=e.comment)
                    if e.key == key else e
                    for e in entries
                ]
                applied.append(key)
            else:
                skipped.append(key)
        else:
            entries.append(EnvEntry(key=key, value=value, comment=None))
            applied.append(key)

    return DefaultsResult(entries=entries, applied=applied, skipped=skipped)


def to_defaults_dotenv(result: DefaultsResult) -> str:
    lines = []
    for entry in result.entries:
        if entry.key is None:
            lines.append(entry.raw or "")
        else:
            lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines) + "\n" if lines else ""
