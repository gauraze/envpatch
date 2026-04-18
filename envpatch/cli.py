"""Main CLI entry point for envpatch."""
import click
from envpatch.cli_validate import validate_cmd
from envpatch.cli_snapshot import snapshot_cmd
from envpatch.cli_audit import audit_cmd
from envpatch.cli_encrypt import encrypt_cmd
from envpatch.cli_watch import watch_cmd
from envpatch.cli_template import template_cmd
from envpatch.cli_schema import schema_cmd
from envpatch.cli_promote import promote_cmd
from envpatch.cli_compare import compare_cmd


@click.group()
def cli():
    """envpatch — diff and sync .env files across environments."""


@cli.command(name="diff")
@click.argument("base", type=click.Path(exists=True))
@click.argument("other", type=click.Path(exists=True))
@click.option("--unchanged", is_flag=True, default=False)
def diff_cmd(base, other, unchanged):
    """Show diff between two .env files."""
    from envpatch.parser import EnvFile
    from envpatch.diff import diff_env_files, ChangeType
    base_env = EnvFile.parse(open(base).read())
    other_env = EnvFile.parse(open(other).read())
    entries = diff_env_files(base_env, other_env, include_unchanged=unchanged)
    for e in entries:
        click.echo(str(e))


cli.add_command(validate_cmd, name="validate")
cli.add_command(snapshot_cmd, name="snapshot")
cli.add_command(audit_cmd, name="audit")
cli.add_command(encrypt_cmd, name="encrypt")
cli.add_command(watch_cmd, name="watch")
cli.add_command(template_cmd, name="template")
cli.add_command(schema_cmd, name="schema")
cli.add_command(promote_cmd, name="promote")
cli.add_command(compare_cmd, name="compare")


def main():
    cli()
