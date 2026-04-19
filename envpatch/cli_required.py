import click
from envpatch.parser import EnvFile
from envpatch.required import check_required


@click.group(name="required")
def required_cmd():
    """Check that required keys exist in an env file."""


@required_cmd.command(name="check")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("-k", "--key", "keys", multiple=True, required=True, help="Required key name")
@click.option("--allow-empty", is_flag=True, default=False, help="Allow empty values")
def required_check(env_file: str, keys: tuple, allow_empty: bool) -> None:
    """Check that KEY(s) are present in ENV_FILE."""
    env = EnvFile.parse(open(env_file).read())
    result = check_required(env, list(keys), allow_empty=allow_empty)
    if result.clean:
        click.echo("All required keys present.")
    else:
        for v in result.violations:
            click.echo(f"  {v}")
        raise SystemExit(1)
