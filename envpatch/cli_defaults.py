"""CLI commands for applying defaults to .env files."""
from __future__ import annotations
import click
from envpatch.parser import EnvFile
from envpatch.defaults import apply_defaults, to_defaults_dotenv


@click.group(name="defaults")
def defaults_cmd():
    """Apply default values to .env files."""


@defaults_cmd.command(name="apply")
@click.argument("env_file")
@click.option("--set", "pairs", multiple=True, metavar="KEY=VALUE",
              help="Default key=value pair (repeatable).")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys with defaults.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Print result without writing.")
def defaults_apply(env_file: str, pairs: tuple, overwrite: bool, dry_run: bool):
    """Apply default KEY=VALUE pairs to ENV_FILE."""
    if not pairs:
        raise click.UsageError("Provide at least one --set KEY=VALUE.")

    defaults: dict = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Invalid format: {pair!r}. Expected KEY=VALUE.")
        k, v = pair.split("=", 1)
        defaults[k.strip()] = v.strip()

    try:
        env = EnvFile.parse(open(env_file).read())
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {env_file}")

    result = apply_defaults(env, defaults, overwrite=overwrite)
    output = to_defaults_dotenv(result)

    if dry_run:
        click.echo(output)
        return

    with open(env_file, "w") as fh:
        fh.write(output)

    for key in result.applied:
        click.echo(f"  applied: {key}")
    for key in result.skipped:
        click.echo(f"  skipped (exists): {key}")
    click.echo(f"Done. {len(result.applied)} applied, {len(result.skipped)} skipped.")
