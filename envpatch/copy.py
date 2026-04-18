from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile


@dataclass
class CopyResult:
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.skipped) == 0


def copy_keys(
    source: EnvFile,
    target: EnvFile,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> tuple[EnvFile, CopyResult]:
    """Copy keys from source into target, returning updated EnvFile and result."""
    result = CopyResult()
    entries = {k: v for k, v in [(e.key, e) for e in target.entries]}

    keys_to_copy = keys if keys is not None else source.keys()

    new_entries = list(target.entries)

    for key in keys_to_copy:
        src_entry = source.get(key)
        if src_entry is None:
            continue
        if key in entries:
            if overwrite:
                new_entries = [
                    src_entry if e.key == key else e for e in new_entries
                ]
                result.overwritten.append(key)
            else:
                result.skipped.append(key)
        else:
            new_entries.append(src_entry)
            result.copied.append(key)

    from envpatch.parser import EnvFile as _EF
    updated = _EF(new_entries)
    return updated, result
