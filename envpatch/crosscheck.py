"""Cross-check two env files against a shared schema of expected keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envpatch.parser import EnvFile


@dataclass
class CrossCheckIssue:
    key: str
    file_a: Optional[str]
    file_b: Optional[str]
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message} (a={self.file_a!r}, b={self.file_b!r})"


@dataclass
class CrossCheckResult:
    issues: List[CrossCheckIssue] = field(default_factory=list)
    checked: int = 0

    @property
    def clean(self) -> bool:
        return len(self.issues) == 0

    @property
    def errors(self) -> List[CrossCheckIssue]:
        return self.issues


def crosscheck_envs(
    env_a: EnvFile,
    env_b: EnvFile,
    required_keys: Optional[List[str]] = None,
    allow_empty: bool = False,
) -> CrossCheckResult:
    """Compare env_a and env_b for a set of required_keys.

    For each key check:
    - Present in both files
    - Non-empty in both (unless allow_empty=True)
    """
    result = CrossCheckResult()

    keys_a: Dict[str, str] = {e.key: e.value for e in env_a.entries if e.key}
    keys_b: Dict[str, str] = {e.key: e.value for e in env_b.entries if e.key}

    universe = required_keys if required_keys is not None else sorted(
        set(keys_a) | set(keys_b)
    )

    for key in universe:
        result.checked += 1
        in_a = key in keys_a
        in_b = key in keys_b
        val_a = keys_a.get(key)
        val_b = keys_b.get(key)

        if not in_a and not in_b:
            result.issues.append(
                CrossCheckIssue(key, None, None, "missing from both files")
            )
        elif not in_a:
            result.issues.append(
                CrossCheckIssue(key, None, val_b, "missing from file A")
            )
        elif not in_b:
            result.issues.append(
                CrossCheckIssue(key, val_a, None, "missing from file B")
            )
        elif not allow_empty:
            if not val_a and not val_b:
                result.issues.append(
                    CrossCheckIssue(key, val_a, val_b, "empty in both files")
                )
            elif not val_a:
                result.issues.append(
                    CrossCheckIssue(key, val_a, val_b, "empty in file A")
                )
            elif not val_b:
                result.issues.append(
                    CrossCheckIssue(key, val_a, val_b, "empty in file B")
                )

    return result
