import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.scope import scope_env, to_scoped_dotenv


@click.group(name="scope")
def scope_cmd():
    """Namespace .env keys with a prefix."""


@scope_cmd.command(name="apply")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("prefix")
@click.option("--keys", "-k", multiple=True, help="Limit to specific keys.")
@click.option("--strip", is_flag=True, default=False, help="Strip existing prefix first.")
@click.option("--output", "-o", default=None, help="Write result to file (default: stdout).")
@click.option("--dry-run", is_flag=True, default=False)
def scope_apply(env_file, prefix, keys, strip, output, dry_run):
    """Apply PREFIX to keys in ENV_FILE."""
    env = EnvFile.parse(Path(env_file).read_text())
    result = scope_env(env, prefix, list(keys) or None, strip_prefix=strip)
    dotenv = to_scoped_dotenv(result)

    if result.skipped:
        click.echo(f"Skipped {len(result.skipped)} key(s): {', '.join(result.skipped)}", err=True)

    if dry_run or output is None:
        click.echo(dotenv)
    else:
        Path(output).write_text(dotenv)
        click.echo(f"Written to {output}")
