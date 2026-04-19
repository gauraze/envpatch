import click
from pathlib import Path
from envpatch.parser import EnvFile
from envpatch.tag import tag_env, to_tagged_dotenv


@click.group(name="tag")
def tag_cmd():
    """Tag env keys with inline labels."""


@tag_cmd.command(name="apply")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--tag", "tags", multiple=True, metavar="KEY=LABEL",
              help="Tag to apply in KEY=LABEL format.")
@click.option("--keys", default=None, help="Comma-separated keys to tag.")
@click.option("--output", default=None, help="Output file (default: overwrite input).")
@click.option("--dry-run", is_flag=True, help="Print result without writing.")
def tag_apply(env_file, tags, keys, output, dry_run):
    """Apply tags to keys in an env file."""
    env = EnvFile.parse(Path(env_file).read_text())
    tag_map = {}
    for t in tags:
        if "=" not in t:
            raise click.BadParameter(f"Invalid tag format: {t!r}. Use KEY=LABEL.")
        k, v = t.split("=", 1)
        tag_map[k.strip()] = v.strip()

    key_list = [k.strip() for k in keys.split(",")] if keys else None
    result = tag_env(env, tag_map, keys=key_list)

    if result.skipped:
        click.echo(f"Skipped keys: {', '.join(result.skipped)}", err=True)

    content = to_tagged_dotenv(env, result)

    if dry_run:
        click.echo(content)
        return

    out_path = Path(output) if output else Path(env_file)
    out_path.write_text(content)
    click.echo(f"Tagged {len(result.tagged)} key(s) in {out_path}")
