"""Validation utilities for .env files and diff entries."""
from dataclasses import dataclass, field
from typing import List, Optional
from envpatch.parser import EnvFile
from envpatch.diff import DiffEntry, ChangeType


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def __str__(self) -> str:
        if not self.issues:
            return "Validation passed with no issues."
        return "\n".join(str(i) for i in self.issues)


IMPORTANT_KEYS = {"DATABASE_URL", "SECRET_KEY", "API_KEY", "TOKEN"}


def validate_env_file(env: EnvFile) -> ValidationResult:
    """Validate a single .env file for common issues."""
    result = ValidationResult()
    for key in env.keys():
        value = env.get(key)
        if value is None or value == "":
            severity = "error" if any(k in key for k in IMPORTANT_KEYS) else "warning"
            result.issues.append(ValidationIssue(key, "Value is empty.", severity))
        if key != key.upper():
            result.issues.append(ValidationIssue(key, "Key should be uppercase.", "warning"))
        if " " in key:
            result.issues.append(ValidationIssue(key, "Key contains spaces.", "error"))
    return result


def validate_patch(changes: List[DiffEntry], target: EnvFile) -> ValidationResult:
    """Validate that a patch can be safely applied to a target env."""
    result = ValidationResult()
    for entry in changes:
        if entry.change_type == ChangeType.REMOVED:
            if any(k in entry.key for k in IMPORTANT_KEYS):
                result.issues.append(
                    ValidationIssue(entry.key, "Removing a potentially critical key.", "warning")
                )
        if entry.change_type == ChangeType.ADDED:
            if entry.new_value == "":
                result.issues.append(
                    ValidationIssue(entry.key, "Adding a key with an empty value.", "warning")
                )
    return result
