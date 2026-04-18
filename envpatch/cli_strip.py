import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.strip import strip_keys, to_stripped_dotenv


@click.group(name="strip")
def strip_cmd():
    """Remove keys from a .env file."""


@strip_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, help="Exact key name to remove.")
@click.option("--prefix", default=None, help="Remove all keys with this prefix.")
@click.option("--suffix", default=None, help="Remove all keys with this suffix.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing.")
@click.option("--output", default=None, help="Write result to this file instead.")
def strip_run(
    env_file: str,
    keys: tuple,
    prefix: str,
    suffix: str,
    dry_run: bool,
    output: str,
):
    """Strip specified keys from ENV_FILE."""
    src = Path(env_file)
    env = EnvFile.parse(src.read_text())
    new_env, result = strip_keys(env, list(keys), prefix=prefix, suffix=suffix)

    if result.removed:
        click.echo("Removed keys:")
        for k in result.removed:
            click.echo(f"  - {k}")
    else:
        click.echo("No keys matched — nothing removed.")
        return

    if dry_run:
        click.echo("[dry-run] No changes written.")
        return

    dest = Path(output) if output else src
    dest.write_text(to_stripped_dotenv(new_env))
    click.echo(f"Written to {dest}")
