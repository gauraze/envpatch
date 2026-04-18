"""Schema validation for .env files against a JSON schema definition."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from envpatch.parser import EnvFile


@dataclass
class SchemaField:
    key: str
    required: bool = True
    pattern: str | None = None
    allowed_values: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class SchemaViolation:
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message}"


@dataclass
class SchemaResult:
    violations: list[SchemaViolation] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return len(self.violations) == 0


def load_schema(data: dict[str, Any]) -> list[SchemaField]:
    fields = []
    for key, meta in data.items():
        fields.append(SchemaField(
            key=key,
            required=meta.get("required", True),
            pattern=meta.get("pattern"),
            allowed_values=meta.get("allowed_values", []),
            description=meta.get("description", ""),
        ))
    return fields


def validate_against_schema(env: EnvFile, schema: list[SchemaField]) -> SchemaResult:
    import re
    result = SchemaResult()
    for field in schema:
        value = env.get(field.key)
        if value is None:
            if field.required:
                result.violations.append(SchemaViolation(field.key, "required key is missing"))
            continue
        if field.allowed_values and value not in field.allowed_values:
            result.violations.append(SchemaViolation(
                field.key,
                f"value {value!r} not in allowed values {field.allowed_values}"
            ))
        if field.pattern and not re.fullmatch(field.pattern, value):
            result.violations.append(SchemaViolation(
                field.key,
                f"value {value!r} does not match pattern {field.pattern!r}"
            ))
    return result
