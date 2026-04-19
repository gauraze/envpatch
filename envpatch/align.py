from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile, EnvEntry


@dataclass
class AlignResult:
    entries: List[EnvEntry]
    changed: bool
    padded_keys: List[str] = field(default_factory=list)

    def clean(self) -> bool:
        return not self.changed


def _max_key_len(entries: List[EnvEntry]) -> int:
    return max((len(e.key) for e in entries if e.key), default=0)


def align_env(env: EnvFile, pad_char: str = " ") -> AlignResult:
    """Align all key=value pairs so the '=' signs line up."""
    entries = list(env.entries)
    value_entries = [e for e in entries if e.key]
    if not value_entries:
        return AlignResult(entries=entries, changed=False)

    width = _max_key_len(value_entries)
    new_entries: List[EnvEntry] = []
    padded: List[str] = []
    changed = False

    for e in entries:
        if not e.key:
            new_entries.append(e)
            continue
        padding = pad_char * (width - len(e.key))
        new_raw = f"{e.key}{padding}={e.value if e.value is not None else ''}"
        if new_raw != e.raw:
            padded.append(e.key)
            changed = True
        new_entries.append(EnvEntry(key=e.key, value=e.value, raw=new_raw, comment=e.comment))

    return AlignResult(entries=new_entries, changed=changed, padded_keys=padded)


def to_aligned_dotenv(result: AlignResult) -> str:
    lines = []
    for e in result.entries:
        if e.comment:
            lines.append(e.comment)
        lines.append(e.raw)
    return "\n".join(lines) + "\n"
