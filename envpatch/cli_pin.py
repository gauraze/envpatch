"""CLI commands for pinning env keys."""
import click
from envpatch.parser import EnvFile
from envpatch.pin import pin_keys, apply_pins


@click.group(name="pin")
def pin_cmd():
    """Pin env keys to exact values."""


@pin_cmd.command(name="check")
@click.argument("env_file")
@click.option("--pin", "pins", multiple=True, metavar="KEY=VALUE",
              help="Key=value pair to pin. Repeatable.")
def pin_check(env_file, pins):
    """Check that pinned keys match expected values."""
    parsed_pins = _parse_pins(pins)
    if not parsed_pins:
        click.echo("No pins specified.")
        return
    env = EnvFile.parse(open(env_file).read())
    result = pin_keys(env, parsed_pins)
    if result.clean:
        click.echo("All pinned keys match.")
    else:
        for v in result.violations:
            click.echo(str(v))
        raise SystemExit(1)


@pin_cmd.command(name="apply")
@click.argument("env_file")
@click.option("--pin", "pins", multiple=True, metavar="KEY=VALUE",
              help="Key=value pair to force. Repeatable.")
@click.option("--dry-run", is_flag=True, default=False)
def pin_apply(env_file, pins, dry_run):
    """Force pinned key values into the env file."""
    parsed_pins = _parse_pins(pins)
    if not parsed_pins:
        click.echo("No pins specified.")
        return
    env = EnvFile.parse(open(env_file).read())
    updated = apply_pins(env, parsed_pins)
    output = updated.serialize()
    if dry_run:
        click.echo(output)
    else:
        with open(env_file, "w") as f:
            f.write(output)
        click.echo(f"Applied {len(parsed_pins)} pin(s) to {env_file}")


def _parse_pins(pins):
    result = {}
    for p in pins:
        if "=" not in p:
            raise click.BadParameter(f"Pin must be KEY=VALUE, got: {p}")
        k, v = p.split("=", 1)
        result[k.strip()] = v.strip()
    return result
