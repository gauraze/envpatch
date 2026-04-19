from __future__ import annotations
import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.trim import trim_env, to_trimmed_dotenv


@click.group(name="trim")
def trim_cmd():
    """Remove keys from a .env file."""


@trim_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, help="Key(s) to remove.")
@click.option("--prefix", "prefixes", multiple=True, help="Remove keys matching prefix.")
@click.option("--empty-only", is_flag=True, default=False, help="Only remove keys with empty values.")
@click.option("--output", "-o", default=None, help="Output file (default: overwrite input).")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
def trim_run(env_file, keys, prefixes, empty_only, output, dry_run):
    """Trim keys from a .env file by name or prefix."""
    env = EnvFile.parse(Path(env_file).read_text())
    result = trim_env(
        env,
        keys=list(keys) or None,
        prefixes=list(prefixes) or None,
        empty_only=empty_only,
    )

    content = to_trimmed_dotenv(result)

    if result.removed:
        click.echo(f"Removed {len(result.removed)} key(s): {', '.join(result.removed)}")
    else:
        click.echo("No keys removed.")

    if dry_run:
        click.echo(content)
        return

    dest = output or env_file
    Path(dest).write_text(content)
    click.echo(f"Written to {dest}")
