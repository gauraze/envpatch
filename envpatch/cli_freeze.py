"""CLI commands for freeze: lock and verify env values."""
import json
import click
from envpatch.parser import EnvFile
from envpatch.freeze import freeze_env, check_freeze


@click.group("freeze")
def freeze_cmd():
    """Lock and verify env key values."""


@freeze_cmd.command("lock")
@click.argument("env_file")
@click.argument("output")
@click.option("--keys", "-k", multiple=True, help="Keys to freeze (default: all)")
def freeze_lock(env_file, output, keys):
    """Freeze current env values to a JSON lock file."""
    env = EnvFile.parse(open(env_file).read())
    frozen = freeze_env(env, list(keys) if keys else None)
    with open(output, "w") as f:
        json.dump(frozen, f, indent=2)
    click.echo(f"Locked {len(frozen)} key(s) to {output}")


@freeze_cmd.command("check")
@click.argument("env_file")
@click.argument("lock_file")
def freeze_check(env_file, lock_file):
    """Check env against a freeze lock file."""
    env = EnvFile.parse(open(env_file).read())
    frozen = json.loads(open(lock_file).read())
    result = check_freeze(env, frozen)
    if result.clean:
        click.echo("OK: all frozen values match.")
    else:
        for v in result.violations:
            click.echo(f"  DRIFT  {v}")
        raise SystemExit(1)
