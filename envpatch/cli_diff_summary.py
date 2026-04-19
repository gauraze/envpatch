import click
from envpatch.parser import EnvFile
from envpatch.diff import diff_env_files
from envpatch.diff_summary import summarize, format_summary_table


@click.group(name="summary")
def summary_cmd():
    """Summarize diff between two .env files."""


@summary_cmd.command(name="show")
@click.argument("base", type=click.Path(exists=True))
@click.argument("other", type=click.Path(exists=True))
@click.option("--show-unchanged", is_flag=True, default=False, help="Include unchanged keys.")
@click.option("--exit-code", is_flag=True, default=False, help="Exit 1 if changes detected.")
def summary_show(base, other, show_unchanged, exit_code):
    """Show a summary of differences between BASE and OTHER."""
    base_env = EnvFile.parse(open(base).read())
    other_env = EnvFile.parse(open(other).read())
    entries = diff_env_files(base_env, other_env, include_unchanged=show_unchanged)
    summary = summarize(entries)
    click.echo(format_summary_table(summary, show_unchanged=show_unchanged))
    if exit_code and not summary.clean:
        raise SystemExit(1)


def main():
    summary_cmd()


if __name__ == "__main__":
    main()
