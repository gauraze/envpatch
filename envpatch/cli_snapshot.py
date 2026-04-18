"""CLI commands for snapshot management."""
from __future__ import annotations

import click

from envpatch.parser import EnvFile
from envpatch.snapshot import load_snapshot, save_snapshot, snapshot_metadata
from envpatch.diff import diff_env_files
from envpatch.export import to_dotenv_patch


@click.group("snapshot")
def snapshot_cmd():
    """Save and compare .env snapshots."""


@snapshot_cmd.command("save")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("snapshot_file", type=click.Path())
@click.option("--label", default=None, help="Human-readable label for this snapshot.")
def snapshot_save(env_file, snapshot_file, label):
    """Save ENV_FILE as a snapshot to SNAPSHOT_FILE."""
    env = EnvFile.parse(open(env_file).read())
    data = save_snapshot(env, snapshot_file, label=label or env_file)
    click.echo(f"Snapshot saved: {data['entry_count'] if 'entry_count' in data else len(data['entries'])} keys → {snapshot_file}")


@snapshot_cmd.command("info")
@click.argument("snapshot_file", type=click.Path(exists=True))
def snapshot_info(snapshot_file):
    """Show metadata for a snapshot file."""
    meta = snapshot_metadata(snapshot_file)
    click.echo(f"Label     : {meta['label']}")
    click.echo(f"Created   : {meta['created_at']}")
    click.echo(f"Keys      : {meta['entry_count']}")
    click.echo(f"Version   : {meta['version']}")


@snapshot_cmd.command("diff")
@click.argument("snapshot_file", type=click.Path(exists=True))
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--patch", is_flag=True, help="Output as .env patch format.")
def snapshot_diff(snapshot_file, env_file, patch):
    """Diff a snapshot against a current ENV_FILE."""
    base = load_snapshot(snapshot_file)
    current = EnvFile.parse(open(env_file).read())
    entries = diff_env_files(base, current)
    if not entries:
        click.echo("No differences found.")
        return
    if patch:
        click.echo(to_dotenv_patch(entries))
    else:
        for e in entries:
            click.echo(str(e))
