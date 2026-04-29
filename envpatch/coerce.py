from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile


@dataclass
class CoerceIssue:
    key: str
    original: str
    coerced: str
    coerce_type: str

    def __str__(self) -> str:
        return f"{self.key}: '{self.original}' -> '{self.coerced}' (as {self.coerce_type})"


@dataclass
class CoerceResult:
    entries: EnvFile
    issues: List[CoerceIssue] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.issues) == 0

    def to_dotenv(self) -> str:
        lines = []
        for entry in self.entries.entries:
            lines.append(f"{entry.key}={entry.value}")
        return "\n".join(lines) + ("\n" if lines else "")


_BOOL_TRUE = {"true", "yes", "1", "on"}
_BOOL_FALSE = {"false", "no", "0", "off"}


def _coerce_value(value: str, coerce_type: str) -> Optional[str]:
    """Return the normalised string form, or None if no change needed."""
    if coerce_type == "bool":
        lower = value.strip().lower()
        if lower in _BOOL_TRUE:
            return "true" if lower != "true" else None
        if lower in _BOOL_FALSE:
            return "false" if lower != "false" else None
        return None
    if coerce_type == "int":
        try:
            normalised = str(int(value.strip()))
            return normalised if normalised != value else None
        except ValueError:
            return None
    if coerce_type == "float":
        try:
            normalised = str(float(value.strip()))
            return normalised if normalised != value else None
        except ValueError:
            return None
    if coerce_type == "str":
        stripped = value.strip()
        return stripped if stripped != value else None
    return None


def coerce_env(env: EnvFile, rules: Dict[str, str]) -> CoerceResult:
    """Coerce values in *env* according to *rules* (key -> type).

    Supported types: bool, int, float, str.
    Keys not present in *rules* are left untouched.
    """
    import copy

    result_entries = copy.deepcopy(env)
    issues: List[CoerceIssue] = []

    for entry in result_entries.entries:
        if entry.key not in rules:
            continue
        coerce_type = rules[entry.key]
        new_val = _coerce_value(entry.value, coerce_type)
        if new_val is not None:
            issues.append(CoerceIssue(
                key=entry.key,
                original=entry.value,
                coerced=new_val,
                coerce_type=coerce_type,
            ))
            entry.value = new_val

    return CoerceResult(entries=result_entries, issues=issues)
