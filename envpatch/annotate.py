"""Annotate .env keys with inline comments."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile


@dataclass
class AnnotateResult:
    entries: List[str] = field(default_factory=list)  # lines of the output dotenv
    annotated: List[str] = field(default_factory=list)  # keys that received a comment
    skipped: List[str] = field(default_factory=list)   # keys with no annotation provided

    @property
    def clean(self) -> bool:
        return len(self.annotated) == 0

    def to_dotenv(self) -> str:
        return "\n".join(self.entries) + "\n" if self.entries else ""


def annotate_env(
    env: EnvFile,
    annotations: Dict[str, str],
    *,
    overwrite: bool = True,
    inline: bool = True,
) -> AnnotateResult:
    """Attach comments to keys in *env* based on *annotations* mapping.

    Parameters
    ----------
    env:         Parsed EnvFile to annotate.
    annotations: Mapping of key -> comment text (without leading ``#``).
    overwrite:   When False, skip keys that already have a comment.
    inline:      When True, place the comment inline (``KEY=value  # comment``).
                 When False, place the comment on the line above the key.
    """
    result = AnnotateResult()
    entries = env._entries  # list[EnvEntry]

    for entry in entries:
        key = entry.key
        if key is None:
            # Blank line or existing standalone comment — keep as-is.
            result.entries.append(entry.raw)
            continue

        comment = annotations.get(key)
        if comment is None:
            result.skipped.append(key)
            _emit(result, entry, comment=None, inline=inline)
            continue

        existing_inline = _extract_inline(entry.raw)
        if existing_inline and not overwrite:
            result.skipped.append(key)
            _emit(result, entry, comment=None, inline=inline)
            continue

        result.annotated.append(key)
        _emit(result, entry, comment=comment, inline=inline)

    return result


def _extract_inline(raw: str) -> Optional[str]:
    """Return the inline comment portion of a raw line, or None."""
    # Avoid splitting inside quoted values by only looking after the value.
    if "#" in raw:
        idx = raw.index("#")
        # Simple heuristic: if there's an '=' before '#' it's likely inline.
        if "=" in raw and raw.index("=") < idx:
            return raw[idx:].strip()
    return None


def _emit(
    result: AnnotateResult,
    entry,
    comment: Optional[str],
    inline: bool,
) -> None:
    raw = entry.raw
    # Strip any existing inline comment for a clean base.
    base = raw
    existing = _extract_inline(raw)
    if existing:
        base = raw[: raw.index(existing)].rstrip()

    if comment is None:
        result.entries.append(raw)
        return

    if inline:
        result.entries.append(f"{base}  # {comment}")
    else:
        result.entries.append(f"# {comment}")
        result.entries.append(base)
