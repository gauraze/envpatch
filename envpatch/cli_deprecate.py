import click
from envpatch.parser import EnvFile
from envpatch.deprecate import deprecate_env, to_deprecate_dotenv


@click.group(name="deprecate")
def deprecate_cmd():
    """Manage deprecated keys in .env files."""


@deprecate_cmd.command("check")
@click.argument("file", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, help="KEY:reason or KEY:reason:replacement")
def deprecate_check(file, keys):
    """Report deprecated keys without modifying the file."""
    env = EnvFile.parse(open(file).read())
    deprecated = _parse_keys(keys)
    _, result = deprecate_env(env, deprecated, apply=False)
    if result.clean:
        click.echo("No deprecated keys found.")
    else:
        for w in result.warnings:
            click.echo(str(w))
        raise SystemExit(1)


@deprecate_cmd.command("apply")
@click.argument("file", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True)
@click.option("--dry-run", is_flag=True)
@click.option("--output", default=None)
def deprecate_apply(file, keys, dry_run, output):
    """Rename or drop deprecated keys."""
    env = EnvFile.parse(open(file).read())
    deprecated = _parse_keys(keys)
    new_env, result = deprecate_env(env, deprecated, apply=True)

    for w in result.warnings:
        click.echo(str(w))
    for old, new in result.renamed.items():
        click.echo(f"  renamed: {old} -> {new}")
    for k in result.dropped:
        click.echo(f"  dropped: {k}")

    if not dry_run:
        dest = output or file
        open(dest, "w").write(to_deprecate_dotenv(new_env))
        click.echo(f"Written to {dest}")


def _parse_keys(keys):
    deprecated = {}
    for k in keys:
        parts = k.split(":")
        key = parts[0]
        reason = parts[1] if len(parts) > 1 else "deprecated"
        replacement = parts[2] if len(parts) > 2 else None
        drop = parts[2] == "DROP" if len(parts) > 2 else False
        deprecated[key] = {"reason": reason, "replacement": None if drop else replacement, "drop": drop}
    return deprecated
