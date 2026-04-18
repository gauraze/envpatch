"""CLI sub-command: watch a .env file for live changes."""
from __future__ import annotations

import click
from pathlib import Path

from envpatch.watch import watch_env_file, WatchEvent


def _print_event(event: WatchEvent) -> None:
    click.echo(f"\n[envpatch] changes detected in {event.path}")
    for entry in event.changes:
        click.echo(f"  {entry}")


@click.group("watch")
def watch_cmd() -> None:
    """Watch .env files for live changes."""


@watch_cmd.command("start")
@click.argument("env_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--interval", default=1.0, show_default=True, help="Poll interval in seconds.")
def watch_start(env_file: str, interval: float) -> None:
    """Watch ENV_FILE and print a diff whenever it changes."""
    path = Path(env_file)
    click.echo(f"Watching {path} (interval={interval}s) — press Ctrl+C to stop")
    try:
        watch_env_file(path, callback=_print_event, interval=interval)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    except KeyboardInterrupt:
        click.echo("\nStopped.")
