"""Tests for envpatch.report module."""
from envpatch.validate import ValidationResult, ValidationIssue
from envpatch.report import render_report, render_patch_report


def test_render_report_no_issues():
    result = ValidationResult()
    output = render_report(result)
    assert "All checks passed" in output
    assert "Validation Report" in output


def test_render_report_with_errors():
    result = ValidationResult(issues=[
        ValidationIssue("SECRET_KEY", "Value is empty.", "error")
    ])
    output = render_report(result)
    assert "Errors" in output
    assert "SECRET_KEY" in output
    assert "1 error" in output


def test_render_report_with_warnings():
    result = ValidationResult(issues=[
        ValidationIssue("host", "Key should be uppercase.", "warning")
    ])
    output = render_report(result)
    assert "Warnings" in output
    assert "host" in output
    assert "1 warning" in output


def test_render_report_mixed():
    result = ValidationResult(issues=[
        ValidationIssue("KEY1", "Empty.", "error"),
        ValidationIssue("key2", "Lowercase.", "warning"),
    ])
    output = render_report(result)
    assert "1 error" in output
    assert "1 warning" in output


def test_render_patch_report_all_clean():
    r1 = ValidationResult()
    r2 = ValidationResult()
    output = render_patch_report(r1, r2)
    assert "All checks passed" in output


def test_render_patch_report_shows_both_sections():
    r1 = ValidationResult(issues=[ValidationIssue("A", "err", "error")])
    r2 = ValidationResult(issues=[ValidationIssue("B", "warn", "warning")])
    output = render_patch_report(r1, r2)
    assert "Target Env Validation" in output
    assert "Patch Validation" in output
    assert "A" in output
    assert "B" in output
