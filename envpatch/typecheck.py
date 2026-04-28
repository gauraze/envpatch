from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile

# Supported type hints for schema-driven type checking
_SUPPORTED_TYPES = {"str", "int", "float", "bool"}


@dataclass
class TypeViolation:
    key: str
    expected: str
    actual_value: str
    reason: str

    def __str__(self) -> str:
        return (
            f"{self.key}: expected {self.expected}, "
            f"got {self.actual_value!r} ({self.reason})"
        )


@dataclass
class TypeCheckResult:
    violations: List[TypeViolation] = field(default_factory=list)
    checked: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0

    @property
    def errors(self) -> List[TypeViolation]:
        return self.violations


def _check_int(value: str) -> Optional[str]:
    try:
        int(value)
        return None
    except ValueError:
        return "not a valid integer"


def _check_float(value: str) -> Optional[str]:
    try:
        float(value)
        return None
    except ValueError:
        return "not a valid float"


def _check_bool(value: str) -> Optional[str]:
    if value.lower() in {"true", "false", "1", "0", "yes", "no"}:
        return None
    return "not a valid boolean (expected true/false/1/0/yes/no)"


_CHECKERS = {
    "int": _check_int,
    "float": _check_float,
    "bool": _check_bool,
}


def typecheck_env(
    env: EnvFile, type_map: Dict[str, str]
) -> TypeCheckResult:
    """Check that values in *env* conform to the types declared in *type_map*.

    Keys absent from *type_map* are ignored.  Unknown type names are skipped
    with a violation noting the unsupported type.
    """
    result = TypeCheckResult()
    for key, expected_type in type_map.items():
        value = env.get(key)
        if value is None:
            continue  # missing keys are not this module's concern
        result.checked.append(key)
        if expected_type == "str":
            # every value is a string — always passes
            continue
        if expected_type not in _SUPPORTED_TYPES:
            result.violations.append(
                TypeViolation(
                    key=key,
                    expected=expected_type,
                    actual_value=value,
                    reason=f"unsupported type '{expected_type}'",
                )
            )
            continue
        checker = _CHECKERS.get(expected_type)
        if checker:
            reason = checker(value)
            if reason:
                result.violations.append(
                    TypeViolation(
                        key=key,
                        expected=expected_type,
                        actual_value=value,
                        reason=reason,
                    )
                )
    return result
