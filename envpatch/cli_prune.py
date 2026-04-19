import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.prune import prune_env, to_pruned_dotenv


@click.group("prune")
def prune_cmd() -> None:
    """Remove unwanted keys from a .env file."""


@prune_cmd.command("run")
@click.argument("file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Write result to this file (default: stdout).")
@click.option("--remove-empty/--keep-empty", default=True, show_default=True, help="Remove keys with empty values.")
@click.option("--remove-comments", is_flag=True, default=False, help="Remove comment lines.")
@click.option("--key", "-k", multiple=True, help="Explicit key(s) to remove.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing.")
def prune_run(
    file: str,
    output: str | None,
    remove_empty: bool,
    remove_comments: bool,
    key: tuple[str, ...],
    dry_run: bool,
) -> None:
    env = EnvFile.parse(Path(file).read_text())
    result = prune_env(
        env,
        remove_empty=remove_empty,
        remove_comments=remove_comments,
        keys=list(key),
    )

    if result.clean:
        click.echo("Nothing to prune.")
        return

    click.echo(f"Pruned {len(result.removed)} key(s):")
    for entry in result.removed:
        label = entry.key or "<comment>"
        click.echo(f"  - {label}")

    content = to_pruned_dotenv(result)

    if dry_run:
        click.echo("\n[dry-run] Output preview:")
        click.echo(content)
        return

    dest = Path(output) if output else Path(file)
    dest.write_text(content)
    click.echo(f"Written to {dest}")
