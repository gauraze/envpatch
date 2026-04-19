from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class RotateResult:
    rotated: Dict[str, str] = field(default_factory=dict)
    skipped: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.rotated) == 0


def rotate_keys(
    env: EnvFile,
    replacements: Dict[str, str],
    keys: Optional[List[str]] = None,
    overwrite: bool = True,
) -> RotateResult:
    """Replace values for specified keys with new values."""
    result = RotateResult()
    target_keys = keys if keys is not None else list(replacements.keys())

    for key in target_keys:
        if key not in replacements:
            result.skipped.append(key)
            continue
        existing = env.get(key)
        if existing is None:
            result.skipped.append(key)
            continue
        if not overwrite and existing == replacements[key]:
            result.skipped.append(key)
            continue
        result.rotated[key] = replacements[key]

    return result


def apply_rotation(env: EnvFile, result: RotateResult) -> EnvFile:
    """Return a new EnvFile with rotated values applied."""
    from envpatch.parser import EnvEntry
    new_entries = []
    for entry in env.entries:
        if entry.key and entry.key in result.rotated:
            new_entries.append(EnvEntry(key=entry.key, value=result.rotated[entry.key], comment=entry.comment))
        else:
            new_entries.append(entry)
    return EnvFile(entries=new_entries)


def to_rotated_dotenv(env: EnvFile, result: RotateResult) -> str:
    updated = apply_rotation(env, result)
    lines = []
    for entry in updated.entries:
        if entry.key is None:
            lines.append(entry.raw or "")
        else:
            line = f"{entry.key}={entry.value}"
            if entry.comment:
                line += f"  # {entry.comment}"
            lines.append(line)
    return "\n".join(lines) + "\n"
