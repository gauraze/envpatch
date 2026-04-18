"""CLI commands for promoting env values between profiles."""
import click
from envpatch.promote import promote_profiles
from envpatch.parser import EnvFile


@click.group(name="promote")
def promote_cmd():
    """Promote .env values across environment profiles."""


@promote_cmd.command(name="run")
@click.argument("source")
@click.argument("target")
@click.option("--base-dir", default=".", show_default=True, help="Profile directory.")
@click.option("--keys", default=None, help="Comma-separated keys to promote.")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite conflicting keys.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview without writing.")
def promote_run(source, target, base_dir, keys, overwrite, dry_run):
    """Promote keys from SOURCE profile to TARGET profile."""
    key_list = [k.strip() for k in keys.split(",")] if keys else None
    updated_env, result = promote_profiles(
        source, target, base_dir=base_dir, keys=key_list, overwrite=overwrite
    )

    click.echo(f"Promoting: {result.source} → {result.target}")
    if result.promoted:
        click.echo(f"  Promoted ({len(result.promoted)}): {', '.join(result.promoted)}")
    if result.skipped:
        click.echo(f"  Skipped  ({len(result.skipped)}): {', '.join(result.skipped)}")
    if result.conflicts and not overwrite:
        click.echo(f"  Conflicts ({len(result.conflicts)}): {', '.join(result.conflicts)}")
        click.echo("  Use --overwrite to force.")

    if dry_run:
        click.echo("[dry-run] No files written.")
        return

    if not result.clean and not overwrite:
        click.echo("Aborted: resolve conflicts or use --overwrite.", err=True)
        raise SystemExit(1)

    import os
    out_path = os.path.join(base_dir, f".env.{target}")
    lines = []
    for k, v in updated_env.data.items():
        comment = updated_env.comments.get(k)
        if comment:
            lines.append(comment)
        lines.append(f"{k}={v}")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    click.echo(f"Written to {out_path}")
