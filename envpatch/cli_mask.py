from __future__ import annotations
import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.mask import mask_env, DEFAULT_MASK


@click.group(name="mask")
def mask_cmd():
    """Mask sensitive values in .env files."""


@mask_cmd.command(name="run")
@click.argument("file", type=click.Path(exists=True))
@click.option("--placeholder", default=DEFAULT_MASK, show_default=True, help="Replacement text.")
@click.option("--key", "keys", multiple=True, help="Explicit keys to mask.")
@click.option("--pattern", "patterns", multiple=True, help="Substring patterns to match key names.")
@click.option("--output", "-o", default=None, help="Write result to file (default: stdout).")
@click.option("--dry-run", is_flag=True, help="Print result without writing.")
def mask_run(file, placeholder, keys, patterns, output, dry_run):
    """Mask sensitive env values."""
    env = EnvFile.parse(Path(file).read_text())
    result = mask_env(
        env,
        patterns=list(patterns) or None,
        placeholder=placeholder,
        keys=list(keys) or None,
    )
    dotenv = result.to_dotenv()

    if result.masked_keys:
        click.echo(f"Masked {len(result.masked_keys)} key(s): {', '.join(result.masked_keys)}", err=True)
    else:
        click.echo("No keys matched for masking.", err=True)

    if dry_run or output is None:
        click.echo(dotenv)
    else:
        Path(output).write_text(dotenv)
        click.echo(f"Written to {output}")
