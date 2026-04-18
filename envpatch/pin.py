"""Pin specific env keys to exact values, preventing accidental changes."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envpatch.parser import EnvFile


@dataclass
class PinViolation:
    key: str
    pinned_value: str
    actual_value: str

    def __str__(self) -> str:
        return f"[PIN] {self.key}: expected '{self.pinned_value}', got '{self.actual_value}'"


@dataclass
class PinResult:
    violations: List[PinViolation] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.violations) == 0


def pin_keys(env: EnvFile, pins: Dict[str, str]) -> PinResult:
    """Check that pinned keys match expected values in env."""
    result = PinResult()
    for key, expected in pins.items():
        actual = env.get(key)
        if actual is None:
            result.violations.append(PinViolation(key, expected, "<missing>"))
        elif actual != expected:
            result.violations.append(PinViolation(key, expected, actual))
    return result


def apply_pins(env: EnvFile, pins: Dict[str, str]) -> EnvFile:
    """Return a new EnvFile with pinned keys forced to their pinned values."""
    from envpatch.parser import EnvEntry
    entries = {e.key: e for e in env.entries}
    for key, value in pins.items():
        entries[key] = EnvEntry(key=key, value=value, comment=None, raw=f"{key}={value}")
    return EnvFile(entries=list(entries.values()))
