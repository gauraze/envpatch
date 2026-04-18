"""Generate human-readable validation reports."""
from typing import List
from envpatch.validate import ValidationResult, ValidationIssue


def _section(title: str, issues: List[ValidationIssue]) -> str:
    if not issues:
        return ""
    lines = [f"  {i.key}: {i.message}" for i in issues]
    return f"{title}:\n" + "\n".join(lines)


def render_report(result: ValidationResult, title: str = "Validation Report") -> str:
    """Render a ValidationResult as a formatted text report."""
    lines = [f"=== {title} ==="]
    if result.valid and not result.warnings:
        lines.append("✓ All checks passed.")
        return "\n".join(lines)

    error_section = _section("Errors", result.errors)
    warning_section = _section("Warnings", result.warnings)

    if error_section:
        lines.append(error_section)
    if warning_section:
        lines.append(warning_section)

    summary_parts = []
    if result.errors:
        summary_parts.append(f"{len(result.errors)} error(s)")
    if result.warnings:
        summary_parts.append(f"{len(result.warnings)} warning(s)")
    lines.append("Summary: " + ", ".join(summary_parts))
    return "\n".join(lines)


def render_patch_report(
    env_result: ValidationResult,
    patch_result: ValidationResult,
) -> str:
    """Combine env and patch validation into one report."""
    sections = []
    if env_result.issues:
        sections.append(render_report(env_result, "Target Env Validation"))
    if patch_result.issues:
        sections.append(render_report(patch_result, "Patch Validation"))
    if not sections:
        return "=== Validation Report ===\n✓ All checks passed."
    return "\n\n".join(sections)
