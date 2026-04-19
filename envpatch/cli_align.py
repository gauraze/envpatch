import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.align import align_env, to_aligned_dotenv


@click.group(name="align")
def align_cmd():
    """Align key=value pairs so '=' signs line up."""


@align_cmd.command(name="run")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (default: overwrite input)")
@click.option("--dry-run", is_flag=True, help="Print result without writing")
@click.option("--pad-char", default=" ", show_default=True, help="Padding character")
def align_run(file, output, dry_run, pad_char):
    """Align a .env file so all '=' signs are at the same column."""
    env = EnvFile.parse(Path(file).read_text())
    result = align_env(env, pad_char=pad_char)

    if not result.changed:
        click.echo("Already aligned, no changes needed.")
        return

    out_text = to_aligned_dotenv(result)

    if dry_run:
        click.echo(out_text)
        return

    dest = Path(output) if output else Path(file)
    dest.write_text(out_text)
    click.echo(f"Aligned {len(result.padded_keys)} key(s) in {dest}")
    for k in result.padded_keys:
        click.echo(f"  padded: {k}")
