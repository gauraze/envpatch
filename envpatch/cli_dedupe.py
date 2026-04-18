import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.dedupe import dedupe_env, to_deduped_dotenv


@click.group(name="dedupe")
def dedupe_cmd():
    """Find and remove duplicate keys from .env files."""


@dedupe_cmd.command(name="check")
@click.argument("file", type=click.Path(exists=True))
def dedupe_check(file: str):
    """Report duplicate keys without modifying the file."""
    env = EnvFile.parse(Path(file).read_text())
    result = dedupe_env(env)
    if result.clean:
        click.echo("No duplicate keys found.")
        return
    for key, indices in result.duplicates.items():
        click.echo(f"DUPLICATE: {key} appears at lines {[i+1 for i in indices]}")
    raise SystemExit(1)


@dedupe_cmd.command(name="fix")
@click.argument("file", type=click.Path(exists=True))
@click.option("--keep", default="last", type=click.Choice(["first", "last"]), show_default=True)
@click.option("--dry-run", is_flag=True, default=False)
def dedupe_fix(file: str, keep: str, dry_run: bool):
    """Remove duplicate keys, keeping first or last occurrence."""
    path = Path(file)
    env = EnvFile.parse(path.read_text())
    result = dedupe_env(env, keep=keep)
    if result.clean:
        click.echo("No duplicates found. File unchanged.")
        return
    output = to_deduped_dotenv(result)
    if dry_run:
        click.echo(output)
    else:
        path.write_text(output)
        removed = sum(len(v) - 1 for v in result.duplicates.values())
        click.echo(f"Removed {removed} duplicate(s) from {file} (kept={keep}).")
