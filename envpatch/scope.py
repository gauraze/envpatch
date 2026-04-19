from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class ScopeResult:
    scoped: Dict[str, str]
    skipped: List[str]
    prefix: str

    @property
    def clean(self) -> bool:
        return len(self.skipped) == 0


def scope_env(
    env: EnvFile,
    prefix: str,
    keys: Optional[List[str]] = None,
    strip_prefix: bool = False,
) -> ScopeResult:
    """Return entries namespaced under *prefix*.

    If *keys* is given only those keys are scoped; others are skipped.
    When *strip_prefix* is True any existing leading prefix is removed
    before the new one is applied.
    """
    scoped: Dict[str, str] = {}
    skipped: List[str] = []
    target_keys = keys if keys is not None else env.keys()

    for k in env.keys():
        if k not in target_keys:
            skipped.append(k)
            continue
        base = k
        if strip_prefix and k.startswith(prefix):
            base = k[len(prefix):]
        new_key = f"{prefix}{base}"
        scoped[new_key] = env.get(k)

    return ScopeResult(scoped=scoped, skipped=skipped, prefix=prefix)


def to_scoped_dotenv(result: ScopeResult) -> str:
    """Serialise scoped entries back to .env format."""
    lines = []
    for k, v in result.scoped.items():
        if " " in v or "#" in v:
            lines.append(f'{k}="{v}"')
        else:
            lines.append(f"{k}={v}")
    return "\n".join(lines) + ("\n" if lines else "")
