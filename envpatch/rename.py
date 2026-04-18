"""Rename keys across an env file with optional dry-run support."""
from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class RenameResult:
    renamed: List[tuple] = field(default_factory=list)   # (old, new)
    skipped: List[tuple] = field(default_factory=list)   # (old, reason)
    output: "EnvFile | None" = None

    @property
    def clean(self) -> bool:
        return len(self.skipped) == 0


def rename_keys(env: EnvFile, mapping: Dict[str, str], overwrite: bool = False) -> RenameResult:
    """Return a new EnvFile with keys renamed according to *mapping*.

    Args:
        env: source EnvFile
        mapping: {old_key: new_key}
        overwrite: if True, overwrite existing key at new_key position
    """
    result = RenameResult()
    entries: List[EnvEntry] = []
    existing_keys = set(env.keys())

    for entry in env.entries:
        old_key = entry.key
        if old_key in mapping:
            new_key = mapping[old_key]
            if new_key in existing_keys and new_key != old_key and not overwrite:
                result.skipped.append((old_key, f"target key '{new_key}' already exists"))
                entries.append(entry)
            else:
                result.renamed.append((old_key, new_key))
                entries.append(EnvEntry(key=new_key, value=entry.value, comment=entry.comment))
        else:
            entries.append(entry)

    result.output = EnvFile(entries=entries)
    return result
