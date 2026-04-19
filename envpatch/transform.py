from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class TransformResult:
    entries: List[EnvEntry]
    changed_keys: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.changed_keys) == 0


def apply_transforms(
    env: EnvFile,
    transforms: Dict[str, Callable[[str], str]],
    keys: Optional[List[str]] = None,
) -> TransformResult:
    """Apply per-key or global transform functions to env values."""
    result_entries: List[EnvEntry] = []
    changed: List[str] = []

    for entry in env.entries:
        if not entry.key:
            result_entries.append(entry)
            continue

        if keys is not None and entry.key not in keys:
            result_entries.append(entry)
            continue

        fn = transforms.get(entry.key) or transforms.get("*")
        if fn is None:
            result_entries.append(entry)
            continue

        new_value = fn(entry.value)
        if new_value != entry.value:
            changed.append(entry.key)
            result_entries.append(EnvEntry(key=entry.key, value=new_value, comment=entry.comment))
        else:
            result_entries.append(entry)

    return TransformResult(entries=result_entries, changed_keys=changed)


def to_transformed_dotenv(result: TransformResult) -> str:
    lines = []
    for entry in result.entries:
        if entry.comment:
            lines.append(entry.comment)
        if entry.key:
            lines.append(f"{entry.key}={entry.value}")
    return "\n".join(lines)
