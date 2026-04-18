from dataclasses import dataclass, field
from typing import List, Dict
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class DupeResult:
    duplicates: Dict[str, List[int]] = field(default_factory=dict)
    cleaned: List[EnvEntry] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.duplicates) == 0


def find_duplicates(env: EnvFile) -> Dict[str, List[int]]:
    """Return a dict of key -> list of line indices where key appears more than once."""
    seen: Dict[str, List[int]] = {}
    for i, entry in enumerate(env.entries):
        if entry.key is None:
            continue
        seen.setdefault(entry.key, []).append(i)
    return {k: v for k, v in seen.items() if len(v) > 1}


def dedupe_env(env: EnvFile, keep: str = "last") -> DupeResult:
    """Remove duplicate keys, keeping either 'first' or 'last' occurrence."""
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    duplicates = find_duplicates(env)
    if not duplicates:
        return DupeResult(duplicates={}, cleaned=list(env.entries))

    seen: Dict[str, int] = {}
    indexed = list(enumerate(env.entries))

    if keep == "last":
        indexed = list(reversed(indexed))

    kept_indices = set()
    for i, entry in indexed:
        if entry.key is None:
            kept_indices.add(i)
        elif entry.key not in seen:
            seen[entry.key] = i
            kept_indices.add(i)

    cleaned = [e for i, e in enumerate(env.entries) if i in kept_indices]
    if keep == "last":
        cleaned = sorted(cleaned, key=lambda e: env.entries.index(e))

    return DupeResult(duplicates=duplicates, cleaned=cleaned)


def to_deduped_dotenv(result: DupeResult) -> str:
    lines = []
    for entry in result.cleaned:
        if entry.key is None:
            lines.append(entry.raw)
        else:
            lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines)
