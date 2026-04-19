import click
from envpatch.parser import EnvFile
from envpatch.normalize import normalize_env


@click.group(name="normalize")
def normalize_cmd():
    """Normalize .env file keys and values."""


@normalize_cmd.command(name="run")
@click.argument("file")
@click.option("--output", "-o", default=None, help="Output file (default: overwrite input)")
@click.option("--dry-run", is_flag=True, help="Print result without writing")
@click.option("--no-uppercase", is_flag=True, help="Skip key uppercasing")
@click.option("--no-strip-quotes", is_flag=True, help="Skip quote stripping")
@click.option("--no-strip-whitespace", is_flag=True, help="Skip whitespace stripping")
@click.option("--keys", default=None, help="Comma-separated list of keys to normalize")
def normalize_run(file, output, dry_run, no_uppercase, no_strip_quotes, no_strip_whitespace, keys):
    """Normalize keys/values in FILE."""
    env = EnvFile.parse(open(file).read())
    key_list = [k.strip() for k in keys.split(",")] if keys else None

    result = normalize_env(
        env,
        uppercase_keys=not no_uppercase,
        strip_quotes=not no_strip_quotes,
        strip_whitespace=not no_strip_whitespace,
        keys=key_list,
    )

    if result.issues:
        for issue in result.issues:
            click.echo(f"  ~ {issue}")
    else:
        click.echo("No normalization needed.")

    content = result.to_dotenv()

    if dry_run:
        click.echo(content)
        return

    dest = output or file
    with open(dest, "w") as f:
        f.write(content)
    click.echo(f"Written to {dest}")
