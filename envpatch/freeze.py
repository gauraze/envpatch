"""Freeze: lock env values to a snapshot and detect drift."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class FreezeViolation:
    key: str
    expected: str
    actual: Optional[str]  # None = missing

    def __str__(self) -> str:
        if self.actual is None:
            return f"{self.key}: frozen but missing in env"
        return f"{self.key}: expected '{self.expected}', got '{self.actual}'"


@dataclass
class FreezeResult:
    violations: List[FreezeViolation] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0


def freeze_env(env: EnvFile, keys: Optional[List[str]] = None) -> Dict[str, str]:
    """Return a frozen snapshot dict of the env (subset if keys provided)."""
    target = keys if keys is not None else list(env.keys())
    return {k: env.get(k) for k in target if env.get(k) is not None}


def check_freeze(env: EnvFile, frozen: Dict[str, str]) -> FreezeResult:
    """Compare env against a frozen dict and return violations."""
    result = FreezeResult()
    for key, expected in frozen.items():
        actual = env.get(key)
        if actual != expected:
            result.violations.append(FreezeViolation(key=key, expected=expected, actual=actual))
    return result
