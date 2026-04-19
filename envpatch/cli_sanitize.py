import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.sanitize import sanitize_env


@click.group(name="sanitize")
def sanitize_cmd():
    """Sanitize .env file values."""


@sanitize_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (default: stdout)")
@click.option("--remove-empty", is_flag=True, default=False, help="Remove keys with empty values")
@click.option("--no-strip-whitespace", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False, help="Print issues without writing")
def sanitize_run(env_file, output, remove_empty, no_strip_whitespace, dry_run):
    """Sanitize an .env file."""
    env = EnvFile.parse(Path(env_file).read_text())
    result = sanitize_env(
        env,
        strip_whitespace=not no_strip_whitespace,
        remove_empty=remove_empty,
    )

    if result.issues:
        click.echo(f"Found {len(result.issues)} issue(s):")
        for issue in result.issues:
            click.echo(f"  ! {issue}")
    else:
        click.echo("No issues found.")

    if dry_run:
        return

    content = result.to_dotenv()
    if output:
        Path(output).write_text(content)
        click.echo(f"Written to {output}")
    else:
        click.echo(content)
