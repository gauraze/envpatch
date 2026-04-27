import click
from envpatch.parser import EnvFile
from envpatch.copy import copy_keys


@click.group(name="copy")
def copy_cmd():
    """Copy keys between .env files."""


@copy_cmd.command(name="run")
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, help="Keys to copy (default: all)")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing")
def copy_run(source, target, keys, overwrite, dry_run):
    """Copy keys from SOURCE into TARGET."""
    try:
        src = EnvFile.parse(open(source).read())
    except Exception as e:
        raise click.ClickException(f"Failed to read source file '{source}': {e}")

    try:
        tgt = EnvFile.parse(open(target).read())
    except Exception as e:
        raise click.ClickException(f"Failed to read target file '{target}': {e}")

    selected = list(keys) if keys else None
    updated, result = copy_keys(src, tgt, keys=selected, overwrite=overwrite)

    if result.copied:
        click.echo(f"Copied: {', '.join(result.copied)}")
    if result.overwritten:
        click.echo(f"Overwritten: {', '.join(result.overwritten)}")
    if result.skipped:
        click.echo(f"Skipped (already exist): {', '.join(result.skipped)}")

    if not result.copied and not result.overwritten:
        click.echo("Nothing to copy.")
        return

    if dry_run:
        click.echo("[dry-run] No changes written.")
        return

    lines = [e.raw for e in updated.entries]
    try:
        with open(target, "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as e:
        raise click.ClickException(f"Failed to write target file '{target}': {e}")
    click.echo(f"Written to {target}")
