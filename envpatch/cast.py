from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class CastIssue:
    key: str
    expected: str
    actual: str

    def __str__(self) -> str:
        return f"{self.key}: expected {self.expected}, got {self.actual!r}"


@dataclass
class CastResult:
    values: Dict[str, object] = field(default_factory=dict)
    issues: List[CastIssue] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.issues) == 0


DEFAULT_SCHEMA: Dict[str, str] = {}


def _cast_value(key: str, raw: str, type_hint: str) -> tuple[object, Optional[CastIssue]]:
    t = type_hint.lower()
    try:
        if t == "int":
            return int(raw), None
        elif t == "float":
            return float(raw), None
        elif t == "bool":
            if raw.lower() in ("true", "1", "yes"):
                return True, None
            elif raw.lower() in ("false", "0", "no"):
                return False, None
            else:
                raise ValueError()
        elif t == "str":
            return raw, None
        else:
            return raw, None
    except (ValueError, TypeError):
        return raw, CastIssue(key=key, expected=type_hint, actual=raw)


def cast_env(env: EnvFile, schema: Dict[str, str]) -> CastResult:
    """Cast env values to typed Python objects according to schema.

    schema maps key -> type hint string: 'int', 'float', 'bool', 'str'
    Keys not in schema are returned as raw strings.
    """
    result = CastResult()
    for key in env.keys():
        raw = env.get(key) or ""
        if key in schema:
            value, issue = _cast_value(key, raw, schema[key])
            result.values[key] = value
            if issue:
                result.issues.append(issue)
        else:
            result.values[key] = raw
    return result
