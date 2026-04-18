"""CLI entry point for envpatch."""
from __future__ import annotations

import sys
from pathlib import Path

import click

from envpatch.diff import ChangeType, diff_env_files
from envpatch.parser import parse_env_file

COLORS = {
    ChangeType.ADDED: "green",
    ChangeType.REMOVED: "red",
    ChangeType.MODIFIED: "yellow",
    ChangeType.UNCHANGED: None,
}


@click.group()
def cli():
    """envpatch — diff and sync .env files across environments."""


@cli.command("diff")
@click.argument("base", type=click.Path(exists=True, path_type=Path))
@click.argument("target", type=click.Path(exists=True, path_type=Path))
@click.option("--unchanged", is_flag=True, default=False, help="Show unchanged keys too.")
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output.")
def diff_cmd(base: Path, target: Path, unchanged: bool, no_color: bool):
    """Show diff between BASE and TARGET .env files."""
    try:
        base_env = parse_env_file(base)
        target_env = parse_env_file(target)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    entries = diff_env_files(base_env, target_env, include_unchanged=unchanged)

    if not entries:
        click.echo("No differences found.")
        return

    for entry in entries:
        color = None if no_color else COLORS.get(entry.change)
        click.echo(click.style(str(entry), fg=color))


def main():
    cli()


if __name__ == "__main__":
    main()
