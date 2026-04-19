"""Inject environment variables from an EnvFile into a command's environment."""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from envpatch.parser import EnvFile


@dataclass
class InjectResult:
    injected: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    returncode: Optional[int] = None

    @property
    def clean(self) -> bool:
        return len(self.skipped) == 0


def inject_env(
    env_file: EnvFile,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> tuple[dict[str, str], InjectResult]:
    """Build an env dict by injecting values from env_file into os.environ."""
    result = InjectResult()
    merged = dict(os.environ)

    entries = env_file.entries if keys is None else [
        e for e in env_file.entries if e.key in keys
    ]

    for entry in entries:
        if entry.key in merged and not overwrite:
            result.skipped.append(entry.key)
        else:
            merged[entry.key] = entry.value
            result.injected.append(entry.key)

    return merged, result


def run_with_env(
    env_file: EnvFile,
    command: List[str],
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> InjectResult:
    """Run a subprocess with the injected environment."""
    merged, result = inject_env(env_file, keys=keys, overwrite=overwrite)
    proc = subprocess.run(command, env=merged)
    result.returncode = proc.returncode
    return result
