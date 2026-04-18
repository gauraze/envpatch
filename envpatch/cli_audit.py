"""CLI commands for viewing the envpatch audit log."""
import click
from envpatch.audit import load_audit


@click.group("audit")
def audit_cmd():
    """View and manage the envpatch audit log."""


@audit_cmd.command("list")
@click.option("--log", default=".envpatch_audit.json", show_default=True,
              help="Path to audit log file.")
@click.option("--action", default=None, help="Filter by action type.")
@click.option("--limit", default=20, show_default=True, help="Max entries to show.")
def audit_list(log: str, action: str, limit: int):
    """List recent audit log entries."""
    try:
        audit_log = load_audit(log)
    except ValueError as exc:
        raise click.ClickException(str(exc))

    entries = audit_log.entries
    if action:
        entries = [e for e in entries if e.action == action]
    entries = entries[-limit:]

    if not entries:
        click.echo("No audit entries found.")
        return

    for e in entries:
        keys_str = ", ".join(e.keys_changed) if e.keys_changed else "(none)"
        source_str = f" <- {e.source}" if e.source else ""
        note_str = f"  [{e.note}]" if e.note else ""
        click.echo(f"{e.timestamp}  {e.action:10s}  {e.target}{source_str}  keys=[{keys_str}]{note_str}")


@audit_cmd.command("clear")
@click.option("--log", default=".envpatch_audit.json", show_default=True)
@click.confirmation_option(prompt="Clear all audit entries?")
def audit_clear(log: str):
    """Clear all audit log entries."""
    import json, os
    if os.path.exists(log):
        with open(log, "w") as fh:
            json.dump({"version": 1, "entries": []}, fh, indent=2)
        click.echo(f"Audit log cleared: {log}")
    else:
        click.echo("No audit log found.")
