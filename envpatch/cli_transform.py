import click
from envpatch.parser import EnvFile
from envpatch.transform import apply_transforms, to_transformed_dotenv
from pathlib import Path


@click.group(name="transform")
def transform_cmd():
    """Transform env values using built-in functions."""


@transform_cmd.command(name="run")
@click.argument("file")
@click.option("--upper", multiple=True, metavar="KEY", help="Uppercase value for KEY (use * for all)")
@click.option("--lower", multiple=True, metavar="KEY", help="Lowercase value for KEY")
@click.option("--strip", "do_strip", multiple=True, metavar="KEY", help="Strip whitespace for KEY")
@click.option("--dry-run", is_flag=True, help="Print result without writing")
def transform_run(file, upper, lower, do_strip, dry_run):
    """Apply transformations to env values."""
    path = Path(file)
    if not path.exists():
        raise click.ClickException(f"File not found: {file}")

    env = EnvFile.parse(path.read_text())
    transforms = {}

    for k in upper:
        transforms[k] = str.upper
    for k in lower:
        transforms[k] = str.lower
    for k in do_strip:
        transforms[k] = str.strip

    if not transforms:
        raise click.ClickException("No transforms specified. Use --upper, --lower, or --strip.")

    result = apply_transforms(env, transforms)
    output = to_transformed_dotenv(result)

    if dry_run:
        click.echo(output)
        click.echo(f"\n# {len(result.changed_keys)} key(s) would be changed: {', '.join(result.changed_keys)}", err=True)
    else:
        path.write_text(output)
        click.echo(f"Transformed {len(result.changed_keys)} key(s): {', '.join(result.changed_keys)}")
