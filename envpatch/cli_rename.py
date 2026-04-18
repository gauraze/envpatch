"""CLI sub-command: envpatch rename"""
import click
from envpatch.parser import EnvFile
from envpatch.rename import rename_keys


@click.group(name="rename")
def rename_cmd():
    """Rename keys in an .env file."""


@rename_cmd.command(name="run")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("-m", "--map", "mappings", multiple=True, metavar="OLD=NEW",
              required=True, help="Key rename mapping, e.g. OLD_KEY=NEW_KEY")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing target key if it already exists")
@click.option("--dry-run", is_flag=True, default=False,
              help="Preview changes without writing")
@click.option("--out", default=None, type=click.Path(),
              help="Write output to this file instead of overwriting input")
def rename_run(env_file: str, mappings, overwrite: bool, dry_run: bool, out):
    """Rename keys in ENV_FILE according to --map OLD=NEW pairs."""
    mapping: dict = {}
    for m in mappings:
        if "=" not in m:
            raise click.BadParameter(f"Invalid mapping '{m}', expected OLD=NEW")
        old, new = m.split("=", 1)
        mapping[old.strip()] = new.strip()

    env = EnvFile.parse(open(env_file).read())
    result = rename_keys(env, mapping, overwrite=overwrite)

    for old, new in result.renamed:
        click.echo(f"  renamed: {old} -> {new}")
    for old, reason in result.skipped:
        click.echo(f"  skipped: {old} ({reason})", err=True)

    if dry_run:
        click.echo("[dry-run] no files written.")
        return

    dest = out or env_file
    with open(dest, "w") as f:
        f.write(result.output.to_dotenv())
    click.echo(f"Written to {dest}")
