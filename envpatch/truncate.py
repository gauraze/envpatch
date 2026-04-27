from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile, EnvEntry


@dataclass
class TruncateResult:
    entries: List[EnvEntry]
    truncated: Dict[str, int]  # key -> original length
    clean: bool = field(init=False)

    def __post_init__(self) -> None:
        self.clean = len(self.truncated) == 0

    def to_dotenv(self) -> str:
        lines = []
        for entry in self.entries:
            if entry.key is None:
                lines.append(entry.raw)
            else:
                lines.append(f"{entry.key}={entry.value}")
        return "\n".join(lines)


def truncate_env(
    env: EnvFile,
    max_length: int,
    keys: Optional[List[str]] = None,
    suffix: str = "",
) -> TruncateResult:
    """Truncate values in an EnvFile to at most max_length characters.

    Args:
        env: The parsed EnvFile to operate on.
        max_length: Maximum allowed value length (after optional suffix).
        keys: If provided, only truncate these keys; otherwise truncate all.
        suffix: Appended to truncated values (e.g. '...'). Must fit within max_length.

    Returns:
        TruncateResult with updated entries and a map of truncated keys.
    """
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= suffix length ({len(suffix)})"
        )

    cut = max_length - len(suffix)
    truncated: Dict[str, int] = {}
    new_entries: List[EnvEntry] = []

    for entry in env.entries:
        if entry.key is None:
            new_entries.append(entry)
            continue

        target = keys is None or entry.key in keys
        value = entry.value or ""

        if target and len(value) > max_length:
            truncated[entry.key] = len(value)
            new_value = value[:cut] + suffix
            new_entries.append(EnvEntry(key=entry.key, value=new_value, raw=f"{entry.key}={new_value}"))
        else:
            new_entries.append(entry)

    return TruncateResult(entries=new_entries, truncated=truncated)
