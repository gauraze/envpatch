import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.filter import filter_keys, to_filtered_dotenv


@click.group(name="filter")
def filter_cmd():
    """Filter keys from a .env file."""


@filter_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--prefix", multiple=True, help="Keep keys with this prefix.")
@click.option("--suffix", multiple=True, help="Keep keys with this suffix.")
@click.option("--contains", default=None, help="Keep keys containing substring.")
@click.option("--key", multiple=True, help="Keep exact key names.")
@click.option("--invert", is_flag=True, help="Invert the filter (exclude matches).")
@click.option("--dry-run", is_flag=True, help="Print result without writing.")
@click.option("--output", default=None, help="Write result to this file.")
def filter_run(env_file, prefix, suffix, contains, key, invert, dry_run, output):
    env = EnvFile.parse(Path(env_file).read_text())
    result = filter_keys(
        env,
        prefixes=list(prefix) or None,
        suffixes=list(suffix) or None,
        contains=contains,
        keys=list(key) or None,
        invert=invert,
    )
    dotenv = to_filtered_dotenv(result)
    click.echo(f"Matched: {len(result.matched)}  Excluded: {len(result.excluded)}")
    if dry_run:
        click.echo(dotenv)
        return
    dest = output or env_file
    Path(dest).write_text(dotenv)
    click.echo(f"Written to {dest}")
