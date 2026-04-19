import pytest
from envpatch.diff import DiffEntry, ChangeType
from envpatch.diff_summary import summarize, format_summary_table, DiffSummary


def make_entry(key, change, old=None, new=None):
    return DiffEntry(key=key, change=change, old_value=old, new_value=new)


def test_summarize_counts_added():
    entries = [make_entry("A", ChangeType.ADDED, new="1")]
    s = summarize(entries)
    assert s.added == 1
    assert s.removed == 0
    assert s.modified == 0


def test_summarize_counts_removed():
    entries = [make_entry("A", ChangeType.REMOVED, old="1")]
    s = summarize(entries)
    assert s.removed == 1


def test_summarize_counts_modified():
    entries = [make_entry("A", ChangeType.MODIFIED, old="1", new="2")]
    s = summarize(entries)
    assert s.modified == 1


def test_summarize_counts_unchanged():
    entries = [make_entry("A", ChangeType.UNCHANGED, new="1")]
    s = summarize(entries)
    assert s.unchanged == 1


def test_clean_when_no_changes():
    entries = [make_entry("A", ChangeType.UNCHANGED, new="1")]
    s = summarize(entries)
    assert s.clean is True


def test_not_clean_when_changes():
    entries = [make_entry("A", ChangeType.ADDED, new="1")]
    s = summarize(entries)
    assert s.clean is False


def test_total_changes():
    entries = [
        make_entry("A", ChangeType.ADDED, new="1"),
        make_entry("B", ChangeType.REMOVED, old="2"),
        make_entry("C", ChangeType.UNCHANGED, new="3"),
    ]
    s = summarize(entries)
    assert s.total_changes == 2


def test_format_table_excludes_unchanged_by_default():
    entries = [
        make_entry("A", ChangeType.ADDED, new="hello"),
        make_entry("B", ChangeType.UNCHANGED, new="world"),
    ]
    s = summarize(entries)
    out = format_summary_table(s)
    assert "A" in out
    assert "B" not in out


def test_format_table_includes_unchanged_when_requested():
    entries = [
        make_entry("A", ChangeType.ADDED, new="hello"),
        make_entry("B", ChangeType.UNCHANGED, new="world"),
    ]
    s = summarize(entries)
    out = format_summary_table(s, show_unchanged=True)
    assert "B" in out


def test_str_summary():
    entries = [make_entry("A", ChangeType.ADDED, new="1")]
    s = summarize(entries)
    assert "+1" in str(s)
