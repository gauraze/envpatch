from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile


@dataclass
class RequiredViolation:
    key: str
    reason: str

    def __str__(self) -> str:
        return f"MISSING {self.key}: {self.reason}"


@dataclass
class RequiredResult:
    violations: List[RequiredViolation] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0


def check_required(
    env: EnvFile,
    required_keys: List[str],
    allow_empty: bool = False,
) -> RequiredResult:
    """Check that all required keys are present and optionally non-empty."""
    violations: List[RequiredViolation] = []
    for key in required_keys:
        value = env.get(key)
        if value is None:
            violations.append(RequiredViolation(key=key, reason="key not present"))
        elif not allow_empty and value.strip() == "":
            violations.append(RequiredViolation(key=key, reason="value is empty"))
    return RequiredResult(violations=violations)


def assert_required(
    env: EnvFile,
    required_keys: List[str],
    allow_empty: bool = False,
) -> None:
    """Raise ValueError if any required keys are missing or empty."""
    result = check_required(env, required_keys, allow_empty=allow_empty)
    if not result.clean:
        msgs = ", ".join(str(v) for v in result.violations)
        raise ValueError(f"Required key violations: {msgs}")
