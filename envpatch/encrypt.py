"""Simple encryption helpers for sensitive .env values using Fernet."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Dict, List

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # pragma: no cover
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

from envpatch.parser import EnvFile


def generate_key() -> str:
    """Generate a new Fernet key and return it as a string."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    return Fernet.generate_key().decode()


def encrypt_values(env: EnvFile, key: str, fields: List[str]) -> Dict[str, str]:
    """Return a dict of field -> encrypted value for the given fields."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    f = Fernet(key.encode())
    result: Dict[str, str] = {}
    for field in fields:
        value = env.get(field)
        if value is None:
            raise KeyError(f"Field '{field}' not found in env file")
        result[field] = f.encrypt(value.encode()).decode()
    return result


def decrypt_values(encrypted: Dict[str, str], key: str) -> Dict[str, str]:
    """Decrypt a dict of field -> encrypted value."""
    if Fernet is None:
        raise RuntimeError("cryptography package is required: pip install cryptography")
    f = Fernet(key.encode())
    result: Dict[str, str] = {}
    for field, ciphertext in encrypted.items():
        try:
            result[field] = f.decrypt(ciphertext.encode()).decode()
        except InvalidToken as exc:
            raise ValueError(f"Failed to decrypt field '{field}': invalid key or data") from exc
    return result


def save_encrypted(encrypted: Dict[str, str], path: Path) -> None:
    """Persist encrypted values to a JSON file."""
    payload = {"version": 1, "fields": encrypted}
    path.write_text(json.dumps(payload, indent=2))


def load_encrypted(path: Path) -> Dict[str, str]:
    """Load encrypted values from a JSON file."""
    data = json.loads(path.read_text())
    if data.get("version") != 1:
        raise ValueError(f"Unsupported encrypted file version: {data.get('version')}")
    return data["fields"]
