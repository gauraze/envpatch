from __future__ import annotations

import click

from envpatch.parser import EnvFile
from envpatch.truncate import truncate_env


@click.group(name="truncate")
def truncate_cmd() -> None:
    """Truncate long values in a .env file."""


@truncate_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--max-length", "-m", required=True, type=int, help="Maximum value length.")
@click.option("--key", "-k", "keys", multiple=True, help="Restrict to specific keys (repeatable).")
@click.option("--suffix", default="", show_default=True, help="Suffix appended to truncated values.")
@click.option("--output", "-o", default=None, type=click.Path(), help="Write result to file (default: overwrite input).")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing.")
def truncate_run(
    env_file: str,
    max_length: int,
    keys: tuple,
    suffix: str,
    output: str | None,
    dry_run: bool,
) -> None:
    """Truncate values in ENV_FILE to at most MAX_LENGTH characters."""
    env = EnvFile.parse(open(env_file).read())
    result = truncate_env(
        env,
        max_length=max_length,
        keys=list(keys) if keys else None,
        suffix=suffix,
    )

    if result.clean:
        click.echo("No values exceeded the maximum length.")
        return

    click.echo(f"Truncated {len(result.truncated)} key(s):")
    for key, orig_len in result.truncated.items():
        click.echo(f"  {key}: {orig_len} -> {max_length} chars")

    if dry_run:
        click.echo("[dry-run] No files written.")
        return

    dest = output or env_file
    with open(dest, "w") as fh:
        fh.write(result.to_dotenv())
    click.echo(f"Written to {dest}")
