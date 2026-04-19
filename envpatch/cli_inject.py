"""CLI commands for inject: run a command with .env variables injected."""
from __future__ import annotations

import click

from envpatch.parser import EnvFile
from envpatch.inject import inject_env, run_with_env


@click.group(name="inject")
def inject_cmd():
    """Inject .env values into a subprocess environment."""


@inject_cmd.command("run")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("command", nargs=-1, required=True)
@click.option("--keys", "-k", multiple=True, help="Only inject these keys.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing env vars.")
def inject_run(env_file, command, keys, overwrite):
    """Run COMMAND with variables from ENV_FILE injected."""
    ef = EnvFile.parse(open(env_file).read())
    result = run_with_env(ef, list(command), keys=list(keys) or None, overwrite=overwrite)
    if result.injected:
        click.echo(f"Injected: {', '.join(result.injected)}")
    if result.skipped:
        click.echo(f"Skipped (already set): {', '.join(result.skipped)}", err=True)
    raise SystemExit(result.returncode or 0)


@inject_cmd.command("show")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--keys", "-k", multiple=True, help="Only show these keys.")
@click.option("--overwrite", is_flag=True, default=False)
def inject_show(env_file, keys, overwrite):
    """Print the merged environment that would be injected (KEY=VALUE)."""
    ef = EnvFile.parse(open(env_file).read())
    merged, result = inject_env(ef, keys=list(keys) or None, overwrite=overwrite)
    for k in result.injected:
        click.echo(f"{k}={merged[k]}")
    if result.skipped:
        click.echo(f"# Skipped: {', '.join(result.skipped)}", err=True)
