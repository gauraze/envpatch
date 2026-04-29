from __future__ import annotations

import sys
from pathlib import Path

import click

from envpatch.parser import EnvFile
from envpatch.coerce import coerce_env


@click.group(name="coerce")
def coerce_cmd() -> None:
    """Coerce and normalise env value types."""


@coerce_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--rule",
    "rules",
    multiple=True,
    metavar="KEY:TYPE",
    help="Coercion rule, e.g. PORT:int or ENABLED:bool. Repeatable.",
)
@click.option(
    "--output", "-o",
    default=None,
    help="Write result to this file instead of stdout.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print what would change without writing.",
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    default=False,
    help="Suppress informational output.",
)
def coerce_run(
    env_file: str,
    rules: tuple,
    output: str | None,
    dry_run: bool,
    quiet: bool,
) -> None:
    """Apply coercion rules to ENV_FILE."""
    if not rules:
        click.echo("No rules provided. Use --rule KEY:TYPE.", err=True)
        sys.exit(1)

    parsed_rules: dict[str, str] = {}
    for rule in rules:
        if ":" not in rule:
            click.echo(f"Invalid rule format '{rule}'. Expected KEY:TYPE.", err=True)
            sys.exit(1)
        key, coerce_type = rule.split(":", 1)
        parsed_rules[key.strip()] = coerce_type.strip().lower()

    env = EnvFile.parse(Path(env_file).read_text())
    result = coerce_env(env, parsed_rules)

    if not quiet:
        if result.clean:
            click.echo("No coercions applied — values already normalised.")
        else:
            for issue in result.issues:
                click.echo(f"  coerced  {issue}")

    if dry_run:
        if not quiet:
            click.echo("Dry run — no files written.")
        return

    dotenv_content = result.to_dotenv()
    dest = Path(output) if output else Path(env_file)
    dest.write_text(dotenv_content)
    if not quiet:
        click.echo(f"Written to {dest}")
