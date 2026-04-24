"""CLI commands for the resolve feature."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import click

from envpatch.parser import EnvFile
from envpatch.resolve import resolve_env


@click.group("resolve")
def resolve_cmd() -> None:
    """Resolve missing env keys from fallback files."""


@resolve_cmd.command("run")
@click.argument("base", type=click.Path(exists=True))
@click.argument("fallbacks", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--keys", "-k", multiple=True, help="Specific keys to resolve.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite non-empty base values.")
@click.option("--output", "-o", default=None, help="Write result to file (default: stdout).")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
def resolve_run(
    base: str,
    fallbacks: List[str],
    keys: tuple,
    overwrite: bool,
    output: str,
    dry_run: bool,
) -> None:
    """Resolve BASE by filling missing keys from FALLBACKS."""
    base_env = EnvFile.parse(Path(base).read_text())
    fallback_envs = [EnvFile.parse(Path(f).read_text()) for f in fallbacks]

    result = resolve_env(
        base=base_env,
        fallbacks=fallback_envs,
        keys=list(keys) if keys else None,
        overwrite=overwrite,
    )

    if result.resolved:
        click.echo(f"Resolved {len(result.resolved)} key(s):")
        for entry in result.resolved:
            click.echo(f"  + {entry.key}={entry.value}")

    if result.unresolved:
        click.echo(f"Unresolved {len(result.unresolved)} key(s):")
        for key in result.unresolved:
            click.echo(f"  ? {key}")

    dotenv_out = result.to_dotenv()

    if dry_run:
        click.echo("\n--- dry run output ---")
        click.echo(dotenv_out)
        return

    dest = output or base
    Path(dest).write_text(dotenv_out)
    click.echo(f"Written to {dest}")

    if not result.clean:
        sys.exit(1)
