"""CLI commands for schema validation."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envpatch.parser import EnvFile
from envpatch.schema import load_schema, validate_against_schema


@click.group(name="schema")
def schema_cmd():
    """Validate .env files against a schema."""


@schema_cmd.command(name="check")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("schema_file", type=click.Path(exists=True))
def schema_check(env_file: str, schema_file: str):
    """Check ENV_FILE against SCHEMA_FILE (JSON)."""
    env = EnvFile.parse(Path(env_file).read_text())
    raw = json.loads(Path(schema_file).read_text())
    schema = load_schema(raw)
    result = validate_against_schema(env, schema)

    if result.valid:
        click.echo(click.style("✔ Schema validation passed.", fg="green"))
        sys.exit(0)
    else:
        click.echo(click.style(f"✘ {len(result.violations)} violation(s) found:", fg="red"))
        for v in result.violations:
            click.echo(f"  {v}")
        sys.exit(1)


@schema_cmd.command(name="generate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output path for schema JSON.")
def schema_generate(env_file: str, output: str | None):
    """Generate a schema skeleton from ENV_FILE."""
    env = EnvFile.parse(Path(env_file).read_text())
    schema_dict = {
        key: {"required": True, "description": "", "pattern": None, "allowed_values": []}
        for key in env.keys()
    }
    content = json.dumps(schema_dict, indent=2)
    if output:
        Path(output).write_text(content)
        click.echo(f"Schema written to {output}")
    else:
        click.echo(content)
