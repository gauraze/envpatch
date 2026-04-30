"""CLI commands for the pivot feature."""
from __future__ import annotations

import click

from envpatch.parser import EnvFile
from envpatch.pivot import pivot_envs


@click.group(name="pivot")
def pivot_cmd() -> None:
    """Transpose multiple .env files into a side-by-side table."""


@pivot_cmd.command(name="show")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--labels",
    default=None,
    help="Comma-separated labels for each file (e.g. dev,staging,prod).",
)
@click.option(
    "--missing",
    default="<missing>",
    show_default=True,
    help="Marker for absent keys.",
)
@click.option(
    "--no-header",
    is_flag=True,
    default=False,
    help="Omit the header row.",
)
def pivot_show(
    files: tuple,
    labels: str | None,
    missing: str,
    no_header: bool,
) -> None:
    """Print a pivot table comparing FILE … side by side."""
    parsed = [EnvFile.parse(open(f).read()) for f in files]

    label_list = labels.split(",") if labels else None

    try:
        result = pivot_envs(parsed, labels=label_list, missing_marker=missing)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    table = result.to_table()
    if no_header:
        table = table[1:]

    if not table:
        click.echo("(no keys found)")
        return

    col_widths = [
        max(len(str(row[c])) for row in table)
        for c in range(len(table[0]))
    ]

    for row in table:
        line = "  ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        click.echo(line)

    if not result.clean:
        click.echo("\n[warn] Some keys are missing in one or more files.", err=True)
