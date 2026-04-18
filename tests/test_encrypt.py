"""Tests for envpatch.encrypt."""

from __future__ import annotations

import pytest

pytest.importorskip("cryptography")

from pathlib import Path
from envpatch.parser import EnvFile, EnvEntry
from envpatch.encrypt import (
    generate_key,
    encrypt_values,
    decrypt_values,
    save_encrypted,
    load_encrypted,
)


def make_env(**kwargs) -> EnvFile:
    entries = [EnvEntry(k, v, f"{k}={v}") for k, v in kwargs.items()]
    return EnvFile(entries)


def test_generate_key_returns_string():
    key = generate_key()
    assert isinstance(key, str)
    assert len(key) > 0


def test_encrypt_decrypt_roundtrip():
    key = generate_key()
    env = make_env(SECRET="mysecret", TOKEN="abc123")
    encrypted = encrypt_values(env, key, ["SECRET", "TOKEN"])
    assert encrypted["SECRET"] != "mysecret"
    decrypted = decrypt_values(encrypted, key)
    assert decrypted["SECRET"] == "mysecret"
    assert decrypted["TOKEN"] == "abc123"


def test_encrypt_missing_field_raises():
    key = generate_key()
    env = make_env(FOO="bar")
    with pytest.raises(KeyError, match="MISSING"):
        encrypt_values(env, key, ["MISSING"])


def test_decrypt_wrong_key_raises():
    key1 = generate_key()
    key2 = generate_key()
    env = make_env(SECRET="value")
    encrypted = encrypt_values(env, key1, ["SECRET"])
    with pytest.raises(ValueError, match="invalid key or data"):
        decrypt_values(encrypted, key2)


def test_save_and_load_roundtrip(tmp_path):
    key = generate_key()
    env = make_env(API_KEY="supersecret")
    encrypted = encrypt_values(env, key, ["API_KEY"])
    path = tmp_path / "secrets.enc.json"
    save_encrypted(encrypted, path)
    loaded = load_encrypted(path)
    decrypted = decrypt_values(loaded, key)
    assert decrypted["API_KEY"] == "supersecret"


def test_load_bad_version(tmp_path):
    import json
    path = tmp_path / "bad.enc.json"
    path.write_text(json.dumps({"version": 99, "fields": {}}))
    with pytest.raises(ValueError, match="Unsupported"):
        load_encrypted(path)
