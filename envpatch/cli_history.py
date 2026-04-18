"""CLI commands for envpatch history."""
from pathlib import Path
import click
from envpatch.history import load_history, filter_history

DEFAULT_HISTORY = Path(".envpatch_history.json")


@click.group("history")
def history_cmd():
    """View .env change history."""


@history_cmd.command("list")
@click.option("--file", "hist_file", default=str(DEFAULT_HISTORY), show_default=True)
@click.option("--source", default=None, help="Filter by source file")
@click.option("--tag", default=None, help="Filter by tag")
def history_list(hist_file: str, source: str, tag: str):
    """List recorded history entries."""
    path = Path(hist_file)
    entries = load_history(path)
    entries = filter_history(entries, source=source, tag=tag)
    if not entries:
        click.echo("No history entries found.")
        return
    for e in entries:
        tag_str = f" [{e.tag}]" if e.tag else ""
        click.echo(f"{e.timestamp}{tag_str}  {e.source} -> {e.target}  ({e.changes} changes)")
        for line in e.summary:
            click.echo(f"  {line}")


@history_cmd.command("show")
@click.argument("index", type=int)
@click.option("--file", "hist_file", default=str(DEFAULT_HISTORY), show_default=True)
def history_show(index: int, hist_file: str):
    """Show details of a single history entry by index (0-based)."""
    path = Path(hist_file)
    entries = load_history(path)
    if not entries:
        click.echo("No history entries found.")
        return
    if index < 0 or index >= len(entries):
        click.echo(f"Index {index} out of range (0-{len(entries) - 1}).")
        raise SystemExit(1)
    e = entries[index]
    tag_str = f" [{e.tag}]" if e.tag else ""
    click.echo(f"Entry {index}: {e.timestamp}{tag_str}")
    click.echo(f"  Source: {e.source}")
    click.echo(f"  Target: {e.target}")
    click.echo(f"  Changes: {e.changes}")
    for line in e.summary:
        click.echo(f"  {line}")


@history_cmd.command("clear")
@click.option("--file", "hist_file", default=str(DEFAULT_HISTORY), show_default=True)
@click.confirmation_option(prompt="Clear all history?")
def history_clear(hist_file: str):
    """Clear all history entries."""
    path = Path(hist_file)
    if path.exists():
        path.unlink()
        click.echo("History cleared.")
    else:
        click.echo("No history file found.")
