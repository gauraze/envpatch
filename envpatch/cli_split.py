from __future__ import annotations
import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.split import split_by_prefix, to_split_dotenv


@click.group(name="split")
def split_cmd():
    """Split a .env file into multiple files by key prefix."""


@split_cmd.command(name="run")
@click.argument("source", type=click.Path(exists=True))
@click.option("--prefix", "-p", multiple=True, required=True, help="Prefix to split on (repeatable).")
@click.option("--outdir", "-o", default=".", show_default=True, help="Output directory for split files.")
@click.option("--sep", default="_", show_default=True, help="Separator between prefix and key.")
@click.option("--no-keep-prefix", is_flag=True, default=False, help="Strip prefix from keys in output.")
@click.option("--dry-run", is_flag=True, default=False, help="Print output without writing files.")
def split_run(source, prefix, outdir, sep, no_keep_prefix, dry_run):
    """Split SOURCE .env by prefixes into separate files."""
    env = EnvFile.parse(Path(source).read_text())
    result = split_by_prefix(env, list(prefix), sep=sep, keep_prefix=not no_keep_prefix)

    out_path = Path(outdir)

    for grp, entries in result.groups.items():
        content = to_split_dotenv(entries)
        dest = out_path / f".env.{grp.lower()}"
        if dry_run:
            click.echo(f"--- {dest} ---")
            click.echo(content)
        else:
            dest.write_text(content)
            click.echo(f"Written: {dest} ({len(entries)} keys)")

    if result.ungrouped:
        dest = out_path / ".env.other"
        content = to_split_dotenv(result.ungrouped)
        if dry_run:
            click.echo(f"--- {dest} ---")
            click.echo(content)
        else:
            dest.write_text(content)
            click.echo(f"Written: {dest} ({len(result.ungrouped)} ungrouped keys)")
