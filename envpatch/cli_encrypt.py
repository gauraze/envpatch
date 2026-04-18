"""CLI commands for encrypting and decrypting .env field values."""

from __future__ import annotations

import click
from pathlib import Path

from envpatch.parser import EnvFile
from envpatch.encrypt import (
    generate_key,
    encrypt_values,
    decrypt_values,
    save_encrypted,
    load_encrypted,
)


@click.group("encrypt")
def encrypt_cmd():
    """Encrypt and decrypt sensitive .env values."""


@encrypt_cmd.command("keygen")
def keygen():
    """Generate a new encryption key."""
    key = generate_key()
    click.echo(key)


@encrypt_cmd.command("seal")
@click.argument("env_file", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
@click.option("--key", required=True, envvar="ENVPATCH_KEY", help="Fernet key string")
@click.option("--field", "fields", multiple=True, required=True, help="Field(s) to encrypt")
def seal(env_file: str, output: str, key: str, fields: tuple):
    """Encrypt selected fields from ENV_FILE into OUTPUT."""
    env = EnvFile.parse(Path(env_file).read_text())
    try:
        encrypted = encrypt_values(env, key, list(fields))
    except KeyError as exc:
        raise click.ClickException(str(exc))
    save_encrypted(encrypted, Path(output))
    click.echo(f"Sealed {len(encrypted)} field(s) → {output}")


@encrypt_cmd.command("reveal")
@click.argument("sealed_file", type=click.Path(exists=True))
@click.option("--key", required=True, envvar="ENVPATCH_KEY", help="Fernet key string")
def reveal(sealed_file: str, key: str):
    """Decrypt and print all fields from a sealed file."""
    try:
        encrypted = load_encrypted(Path(sealed_file))
        decrypted = decrypt_values(encrypted, key)
    except (ValueError, Exception) as exc:
        raise click.ClickException(str(exc))
    for field, value in decrypted.items():
        click.echo(f"{field}={value}")
