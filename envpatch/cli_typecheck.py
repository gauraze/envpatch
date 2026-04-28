from __future__ import annotations

import json
import sys

import click

from envpatch.parser import EnvFile
from envpatch.typecheck import typecheck_env


@click.group(name="typecheck")
def typecheck_cmd() -> None:
    """Type-check .env values against declared types."""


@typecheck_cmd.command(name="check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--types",
    required=True,
    help='JSON object mapping keys to types, e.g. \'{"PORT":"int","DEBUG":"bool"}\'',
)
@click.option("--quiet", is_flag=True, default=False, help="Suppress output on success.")
def typecheck_check(env_file: str, types: str, quiet: bool) -> None:
    """Check that values in ENV_FILE match the declared --types."""
    try:
        type_map: dict = json.loads(types)
    except json.JSONDecodeError as exc:
        click.echo(f"[error] --types is not valid JSON: {exc}", err=True)
        sys.exit(2)

    env = EnvFile.parse(open(env_file).read())
    result = typecheck_env(env, type_map)

    if result.clean:
        if not quiet:
            click.echo(
                f"[ok] all {len(result.checked)} checked key(s) passed type validation."
            )
        sys.exit(0)

    click.echo(f"[fail] {len(result.violations)} type violation(s) found:", err=True)
    for v in result.violations:
        click.echo(f"  - {v}", err=True)
    sys.exit(1)
