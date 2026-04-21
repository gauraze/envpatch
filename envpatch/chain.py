"""Chain multiple env transformations in a single pass."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Tuple

from envpatch.parser import EnvFile


TransformFn = Callable[[EnvFile], EnvFile]


@dataclass
class ChainStep:
    name: str
    fn: TransformFn


@dataclass
class ChainResult:
    env: EnvFile
    steps_applied: List[str] = field(default_factory=list)
    steps_skipped: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return len(self.steps_skipped) == 0

    def summary(self) -> str:
        lines: List[str] = []
        if self.steps_applied:
            lines.append("Applied: " + ", ".join(self.steps_applied))
        if self.steps_skipped:
            lines.append("Skipped: " + ", ".join(self.steps_skipped))
        return "\n".join(lines) if lines else "No steps configured."


def build_chain(steps: List[Tuple[str, TransformFn]]) -> List[ChainStep]:
    """Build an ordered list of ChainStep objects from (name, fn) tuples."""
    return [ChainStep(name=name, fn=fn) for name, fn in steps]


def run_chain(env: EnvFile, steps: List[ChainStep]) -> ChainResult:
    """Apply each step in sequence, accumulating results.

    A step is skipped (and recorded) if it raises a ValueError.
    Any other exception propagates immediately.
    """
    result = ChainResult(env=env)
    current = env

    for step in steps:
        try:
            current = step.fn(current)
            result.steps_applied.append(step.name)
        except ValueError:
            result.steps_skipped.append(step.name)

    result.env = current
    return result
