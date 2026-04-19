import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.rotate import rotate_keys, to_rotated_dotenv


@click.group(name="rotate")
def rotate_cmd():
    """Rotate (replace) key values in an env file."""


@rotate_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--set", "pairs", multiple=True, metavar="KEY=VALUE", help="Key=value pairs to rotate in.")
@click.option("--keys", "key_filter", default=None, help="Comma-separated keys to limit rotation.")
@click.option("--no-overwrite", is_flag=True, default=False, help="Skip keys that already have the new value.")
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--output", default=None, type=click.Path())
def rotate_run(env_file, pairs, key_filter, no_overwrite, dry_run, output):
    if not pairs:
        click.echo("No --set pairs provided.", err=True)
        raise SystemExit(1)

    replacements = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid pair (missing '='): {pair}", err=True)
            raise SystemExit(1)
        k, v = pair.split("=", 1)
        replacements[k.strip()] = v.strip()

    keys = [k.strip() for k in key_filter.split(",")] if key_filter else None
    env = EnvFile.parse(Path(env_file).read_text())
    result = rotate_keys(env, replacements, keys=keys, overwrite=not no_overwrite)

    if result.clean:
        click.echo("Nothing rotated.")
        return

    for key, val in result.rotated.items():
        click.echo(f"rotated: {key}")
    for key in result.skipped:
        click.echo(f"skipped: {key}")

    if dry_run:
        return

    out = to_rotated_dotenv(env, result)
    dest = Path(output) if output else Path(env_file)
    dest.write_text(out)
    click.echo(f"Written to {dest}")
