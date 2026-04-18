import click
from envpatch.parser import EnvFile
from envpatch.group import group_by_prefix, to_grouped_dotenv


@click.group(name="group")
def group_cmd():
    """Group and organize .env keys by prefix."""


@group_cmd.command(name="show")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--sep", default="_", show_default=True, help="Prefix separator")
def group_show(env_file: str, sep: str):
    """Display keys grouped by prefix."""
    env = EnvFile.parse(open(env_file).read())
    result = group_by_prefix(env, sep=sep)

    for group, keys in result.groups.items():
        click.echo(f"[{group}]")
        for key in keys:
            click.echo(f"  {key}")

    if result.ungrouped:
        click.echo("[other]")
        for key in result.ungrouped:
            click.echo(f"  {key}")


@group_cmd.command(name="sort")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--sep", default="_", show_default=True, help="Prefix separator")
@click.option("--output", "-o", default=None, help="Output file (default: stdout)")
def group_sort(env_file: str, sep: str, output):
    """Rewrite .env file with keys grouped by prefix."""
    env = EnvFile.parse(open(env_file).read())
    result = group_by_prefix(env, sep=sep)
    content = to_grouped_dotenv(env, result, sep=sep)

    if output:
        with open(output, "w") as f:
            f.write(content)
        click.echo(f"Written to {output}")
    else:
        click.echo(content)
