"""CLI commands for template generation and checking."""
from __future__ import annotations
import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.template import to_template, check_template


@click.group("template")
def template_cmd() -> None:
    """Generate and check .env.example templates."""


@template_cmd.command("generate")
@click.argument("source", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (default: stdout)")
@click.option("--placeholder", default="", show_default=True, help="Placeholder value")
@click.option("--keep-values", is_flag=True, default=False, help="Keep original values")
def generate(source: str, output: Optional[str], placeholder: str, keep_values: bool) -> None:  # type: ignore[name-defined]
    """Generate a .env.example from SOURCE."""
    env = EnvFile.parse(Path(source).read_text())
    result = to_template(env, placeholder=placeholder, mask_values=not keep_values)
    if output:
        Path(output).write_text(result + "\n")
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


@template_cmd.command("check")
@click.argument("template", type=click.Path(exists=True))
@click.argument("target", type=click.Path(exists=True))
def check(template: str, target: str) -> None:
    """Check TARGET against TEMPLATE for missing or extra keys."""
    tmpl_env = EnvFile.parse(Path(template).read_text())
    tgt_env = EnvFile.parse(Path(target).read_text())
    report = check_template(tmpl_env, tgt_env)

    if report["missing"]:
        click.echo("Missing keys:")
        for k in report["missing"]:
            click.echo(f"  - {k}")
    if report["extra"]:
        click.echo("Extra keys:")
        for k in report["extra"]:
            click.echo(f"  + {k}")
    if not report["missing"] and not report["extra"]:
        click.echo("OK: target matches template.")
    else:
        raise SystemExit(1)


from typing import Optional  # noqa: E402
