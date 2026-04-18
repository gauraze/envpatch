"""Template generation: create .env.example from an EnvFile."""
from __future__ import annotations
from typing import Optional
from envpatch.parser import EnvFile, EnvEntry


def to_template(
    env: EnvFile,
    placeholder: str = "",
    mask_values: bool = True,
    keep_comments: bool = True,
) -> str:
    """Return a .env.example string from *env*.

    Args:
        env: Parsed source env file.
        placeholder: Value to use for every key (default: empty string).
        mask_values: When True replace values with *placeholder*.
        keep_comments: Preserve inline comments from source.
    """
    lines: list[str] = []
    for entry in env.entries:
        comment = f"  # {entry.comment}" if keep_comments and entry.comment else ""
        value = placeholder if mask_values else entry.value
        lines.append(f"{entry.key}={value}{comment}")
    return "\n".join(lines)


def missing_keys(template: EnvFile, target: EnvFile) -> list[str]:
    """Return keys present in *template* but absent from *target*."""
    template_keys = set(template.keys())
    target_keys = set(target.keys())
    return sorted(template_keys - target_keys)


def extra_keys(template: EnvFile, target: EnvFile) -> list[str]:
    """Return keys present in *target* but absent from *template*."""
    template_keys = set(template.keys())
    target_keys = set(target.keys())
    return sorted(target_keys - template_keys)


def check_template(
    template: EnvFile, target: EnvFile
) -> dict[str, list[str]]:
    """Compare *target* against *template* and return a report dict."""
    return {
        "missing": missing_keys(template, target),
        "extra": extra_keys(template, target),
    }
