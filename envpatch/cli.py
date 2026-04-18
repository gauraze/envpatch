"""Main CLI entry point for envpatch."""
import click

from envpatch.parser import EnvFile
from envpatch.diff import diff_env_files
from envpatch.cli_validate import validate_cmd
from envpatch.cli_snapshot import snapshot_cmd


@click.group()
def cli():
    """envpatch — diff and sync .env files across environments."""


@cli.command("diff")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("other_file", type=click.Path(exists=True))
@click.option("--include-unchanged", is_flag=True, default=False)
def diff_cmd(base_file, other_file, include_unchanged):
    """Show diff between BASE_FILE and OTHER_FILE."""
    base = EnvFile.parse(open(base_file).read())
    other = EnvFile.parse(open(other_file).read())
    entries = diff_env_files(base, other, include_unchanged=include_unchanged)
    if not entries:
        click.echo("No differences found.")
        return
    for e in entries:
        click.echo(str(e))


cli.add_command(validate_cmd, name="validate")
cli.add_command(snapshot_cmd, name="snapshot")


def main():
    cli()


if __name__ == "__main__":
    main()
