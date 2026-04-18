"""CLI commands for comparing env files."""
import click
from envpatch.parser import EnvFile
from envpatch.compare import compare_envs, compare_summary
from envpatch.diff import ChangeType


@click.group(name="compare")
def compare_cmd():
    """Compare two .env files side-by-side."""


@compare_cmd.command(name="run")
@click.argument("base", type=click.Path(exists=True))
@click.argument("other", type=click.Path(exists=True))
@click.option("--unchanged", is_flag=True, default=False, help="Include unchanged keys.")
@click.option("--summary", "show_summary", is_flag=True, default=False, help="Show summary only.")
def compare_run(base, other, unchanged, show_summary):
    """Compare BASE and OTHER env files."""
    base_env = EnvFile.parse(open(base).read())
    other_env = EnvFile.parse(open(other).read())
    result = compare_envs(base_env, other_env, base_name=base, other_name=other, include_unchanged=unchanged)

    if show_summary:
        s = compare_summary(result)
        click.echo(f"Added: {s['added']}  Removed: {s['removed']}  Modified: {s['modified']}  Unchanged: {s['unchanged']}")
        return

    if result.is_identical:
        click.echo("Files are identical.")
        return

    symbols = {ChangeType.ADDED: "+", ChangeType.REMOVED: "-", ChangeType.MODIFIED: "~", ChangeType.UNCHANGED: " "}
    for entry in result.entries:
        sym = symbols[entry.change]
        if entry.change == ChangeType.MODIFIED:
            click.echo(f"{sym} {entry.key}: {entry.old_value!r} -> {entry.new_value!r}")
        elif entry.change == ChangeType.ADDED:
            click.echo(f"{sym} {entry.key}={entry.new_value!r}")
        elif entry.change == ChangeType.REMOVED:
            click.echo(f"{sym} {entry.key}={entry.old_value!r}")
        else:
            click.echo(f"{sym} {entry.key}")
