"""Lint .env files for common style and correctness issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from envpatch.parser import EnvFile


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str = "warning"  # "error" | "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_env_file(env: EnvFile, strict: bool = False) -> LintResult:
    """Run lint checks on an EnvFile. If strict=True, warnings become errors."""
    issues: List[LintIssue] = []

    for key in env.keys():
        value = env.get(key) or ""

        # Duplicate keys are caught at parse time; check key naming conventions
        if key != key.upper():
            issues.append(LintIssue(key, "key should be uppercase", "warning"))

        if " " in key:
            issues.append(LintIssue(key, "key contains spaces", "error"))

        if key.startswith("_"):
            issues.append(LintIssue(key, "key starts with underscore", "warning"))

        if value != value.strip():
            issues.append(LintIssue(key, "value has leading or trailing whitespace", "warning"))

        if len(value) > 512:
            issues.append(LintIssue(key, "value exceeds 512 characters", "warning"))

        if "\n" in value:
            issues.append(LintIssue(key, "value contains newline character", "error"))

    if strict:
        for issue in issues:
            issue.severity = "error"

    return LintResult(issues=issues)
