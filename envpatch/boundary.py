"""boundary.py — enforce key naming boundaries (allowed prefixes/suffixes)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from envpatch.parser import EnvFile


@dataclass
class BoundaryViolation:
    key: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.reason}"


@dataclass
class BoundaryResult:
    violations: List[BoundaryViolation] = field(default_factory=list)
    checked: int = 0

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0

    @property
    def errors(self) -> List[BoundaryViolation]:
        return self.violations


def check_boundaries(
    env: EnvFile,
    allowed_prefixes: Optional[List[str]] = None,
    allowed_suffixes: Optional[List[str]] = None,
    denied_prefixes: Optional[List[str]] = None,
    denied_suffixes: Optional[List[str]] = None,
) -> BoundaryResult:
    """Check that all keys conform to the given naming boundaries."""
    violations: List[BoundaryViolation] = []
    keys = env.keys()

    for key in keys:
        if allowed_prefixes:
            if not any(key.startswith(p) for p in allowed_prefixes):
                violations.append(
                    BoundaryViolation(
                        key=key,
                        reason=f"does not start with any allowed prefix: {allowed_prefixes}",
                    )
                )
                continue

        if allowed_suffixes:
            if not any(key.endswith(s) for s in allowed_suffixes):
                violations.append(
                    BoundaryViolation(
                        key=key,
                        reason=f"does not end with any allowed suffix: {allowed_suffixes}",
                    )
                )
                continue

        if denied_prefixes:
            for p in denied_prefixes:
                if key.startswith(p):
                    violations.append(
                        BoundaryViolation(
                            key=key,
                            reason=f"starts with denied prefix: {p!r}",
                        )
                    )
                    break

        if denied_suffixes:
            for s in denied_suffixes:
                if key.endswith(s):
                    violations.append(
                        BoundaryViolation(
                            key=key,
                            reason=f"ends with denied suffix: {s!r}",
                        )
                    )
                    break

    return BoundaryResult(violations=violations, checked=len(keys))
