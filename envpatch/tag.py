from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class TagResult:
    tagged: Dict[str, List[str]]  # key -> list of tags
    skipped: List[str]

    @property
    def clean(self) -> bool:
        return len(self.skipped) == 0


def tag_env(
    env: EnvFile,
    tags: Dict[str, str],  # key -> tag
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> TagResult:
    """Attach tags (labels) to env keys as inline comments."""
    target_keys = keys if keys is not None else list(env.keys())
    tagged: Dict[str, List[str]] = {}
    skipped: List[str] = []

    for key in target_keys:
        if env.get(key) is None:
            skipped.append(key)
            continue
        tag = tags.get(key)
        if tag is None:
            skipped.append(key)
            continue
        tagged.setdefault(key, []).append(tag)

    return TagResult(tagged=tagged, skipped=skipped)


def to_tagged_dotenv(env: EnvFile, result: TagResult) -> str:
    lines = []
    for entry in env._entries:
        if entry.key and entry.key in result.tagged:
            tag_str = ", ".join(result.tagged[entry.key])
            lines.append(f"{entry.key}={entry.raw_value}  # [{tag_str}]")
        else:
            lines.append(entry.raw_line)
    return "\n".join(lines) + "\n"
