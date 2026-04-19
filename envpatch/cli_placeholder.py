import click
from envpatch.parser import EnvFile
from envpatch.placeholder import check_placeholders


@click.group(name="placeholder")
def placeholder_cmd():
    """Check for placeholder or unset values in .env files."""


@placeholder_cmd.command(name="check")
@click.argument("path")
@click.option("--key", "keys", multiple=True, help="Limit check to specific keys.")
@click.option("--pattern", "patterns", multiple=True, help="Custom placeholder patterns.")
@click.option("--quiet", is_flag=True, default=False, help="Suppress output on success.")
def placeholder_check(path: str, keys, patterns, quiet: bool):
    """Report keys whose values look like placeholders."""
    try:
        env = EnvFile.parse(open(path).read())
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {path}")

    result = check_placeholders(
        env,
        patterns=list(patterns) if patterns else None,
        keys=list(keys) if keys else None,
    )

    if result.clean:
        if not quiet:
            click.echo("No placeholder values detected.")
        raise SystemExit(0)

    for issue in result.issues:
        click.echo(f"  PLACEHOLDER  {issue}")
    raise SystemExit(1)
