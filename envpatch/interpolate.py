"""Variable interpolation for .env files."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import EnvFile

_VAR_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}|\$([A-Z_][A-Z0-9_]*)")


@dataclass
class InterpolateResult:
    entries: Dict[str, str]
    unresolved: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.unresolved) == 0


def _resolve(value: str, context: Dict[str, str], seen: set) -> tuple[str, list]:
    unresolved = []

    def replacer(m: re.Match) -> str:
        key = m.group(1) or m.group(2)
        if key in seen:
            unresolved.append(key)
            return m.group(0)
        if key in context:
            seen.add(key)
            resolved, inner = _resolve(context[key], context, seen)
            unresolved.extend(inner)
            seen.discard(key)
            return resolved
        unresolved.append(key)
        return m.group(0)

    result = _VAR_RE.sub(replacer, value)
    return result, unresolved


def interpolate(env: EnvFile, extra: Dict[str, str] | None = None) -> InterpolateResult:
    """Resolve ${VAR} and $VAR references within an EnvFile.

    Args:
        env: Parsed env file.
        extra: Additional variables to use as context (e.g. OS env).

    Returns:
        InterpolateResult with resolved values and any unresolved references.
    """
    context: Dict[str, str] = {}
    if extra:
        context.update(extra)
    for key in env.keys():
        context[key] = env.get(key) or ""

    resolved: Dict[str, str] = {}
    all_unresolved: List[str] = []

    for key in env.keys():
        value = context.get(key, "")
        result, unresolved = _resolve(value, context, {key})
        resolved[key] = result
        all_unresolved.extend(u for u in unresolved if u not in all_unresolved)

    return InterpolateResult(entries=resolved, unresolved=all_unresolved)
