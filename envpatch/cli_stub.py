"""CLI commands for stub generation."""
from __future__ import annotations
import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.stub import stub_env, to_stub_dotenv


@click.group(name="stub")
def stub_cmd() -> None:
    """Generate stub .env files from key lists."""


@stub_cmd.command(name="generate")
@click.argument("keys", nargs=-1, required=True)
@click.option("--output", "-o", default=None, help="Output file path.")
@click.option("--placeholder", "-p", default="", show_default=True, help="Placeholder value.")
@click.option("--base", "-b", default=None, help="Existing .env to merge into.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--dry-run", is_flag=True, default=False, help="Print result without writing.")
def stub_generate(
    keys: tuple[str, ...],
    output: str | None,
    placeholder: str,
    base: str | None,
    overwrite: bool,
    dry_run: bool,
) -> None:
    """Generate stub entries for KEY [KEY ...]."""
    existing: EnvFile | None = None
    if base:
        base_path = Path(base)
        if not base_path.exists():
            raise click.ClickException(f"Base file not found: {base}")
        existing = EnvFile.parse(base_path.read_text())

    result = stub_env(list(keys), placeholder=placeholder, existing=existing, overwrite=overwrite)
    dotenv = to_stub_dotenv(result)

    if dry_run or output is None:
        click.echo(dotenv, nl=False)
        if result.generated:
            click.echo(f"# Generated: {', '.join(result.generated)}", err=True)
        return

    Path(output).write_text(dotenv)
    click.echo(f"Wrote {len(result.entries)} entries to {output}")
    if result.generated:
        click.echo(f"Stubbed: {', '.join(result.generated)}")
