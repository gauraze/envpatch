"""CLI subcommand for validating .env files and patches."""
import click
from envpatch.parser import EnvFile
from envpatch.diff import diff_env_files
from envpatch.validate import validate_env_file, validate_patch
from envpatch.report import render_report, render_patch_report


@click.command("validate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--against",
    type=click.Path(exists=True),
    default=None,
    help="Optional second .env file to validate a patch against.",
)
def validate_cmd(env_file: str, against: str):
    """Validate an .env file for common issues.

    Optionally validate a patch by providing a second file with --against.
    """
    with open(env_file) as f:
        target = EnvFile.parse(f.read())

    env_result = validate_env_file(target)

    if against:
        with open(against) as f:
            source = EnvFile.parse(f.read())
        changes = diff_env_files(source, target)
        patch_result = validate_patch(changes, target)
        report = render_patch_report(env_result, patch_result)
        click.echo(report)
        if not env_result.valid or not patch_result.valid:
            raise SystemExit(1)
    else:
        report = render_report(env_result)
        click.echo(report)
        if not env_result.valid:
            raise SystemExit(1)
