from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class DeprecationWarning_:
    key: str
    reason: str
    replacement: Optional[str] = None

    def __str__(self) -> str:
        msg = f"[DEPRECATED] {self.key}: {self.reason}"
        if self.replacement:
            msg += f" -> use '{self.replacement}' instead"
        return msg


@dataclass
class DeprecateResult:
    warnings: List[DeprecationWarning_] = field(default_factory=list)
    renamed: Dict[str, str] = field(default_factory=dict)  # old -> new
    dropped: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.warnings


def deprecate_env(
    env: EnvFile,
    deprecated: Dict[str, Dict],  # key -> {reason, replacement, drop}
    apply: bool = False,
) -> tuple[EnvFile, DeprecateResult]:
    """
    Mark keys as deprecated. Optionally rename or drop them.
    deprecated dict format: {KEY: {reason: str, replacement: str|None, drop: bool}}
    """
    result = DeprecateResult()
    entries = list(env.entries)

    for key, meta in deprecated.items():
        if key not in env.keys():
            continue
        reason = meta.get("reason", "deprecated")
        replacement = meta.get("replacement")
        drop = meta.get("drop", False)
        result.warnings.append(DeprecationWarning_(key, reason, replacement))

        if apply:
            if drop:
                entries = [e for e in entries if e.key != key]
                result.dropped.append(key)
            elif replacement:
                for e in entries:
                    if e.key == key:
                        e.key = replacement
                result.renamed[key] = replacement

    from envpatch.parser import EnvFile as EF
    new_env = EF(entries)
    return new_env, result


def to_deprecate_dotenv(env: EnvFile) -> str:
    lines = []
    for e in env.entries:
        if e.comment:
            lines.append(e.comment)
        else:
            lines.append(f"{e.key}={e.value}")
    return "\n".join(lines)
