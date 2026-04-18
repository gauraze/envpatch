from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envpatch.parser import EnvFile


@dataclass
class GroupResult:
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def all_keys(self) -> List[str]:
        result = []
        for keys in self.groups.values():
            result.extend(keys)
        result.extend(self.ungrouped)
        return result


def group_by_prefix(env: EnvFile, sep: str = "_") -> GroupResult:
    """Group keys by their first prefix segment."""
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for key in env.keys():
        if sep in key:
            prefix = key.split(sep, 1)[0]
            groups.setdefault(prefix, []).append(key)
        else:
            ungrouped.append(key)

    return GroupResult(groups=groups, ungrouped=ungrouped)


def group_by_keys(env: EnvFile, mapping: Dict[str, List[str]]) -> GroupResult:
    """Group keys by explicit mapping of group_name -> list of keys."""
    assigned: set = set()
    groups: Dict[str, List[str]] = {}

    for group_name, keys in mapping.items():
        matched = [k for k in keys if env.get(k) is not None]
        if matched:
            groups[group_name] = matched
            assigned.update(matched)

    ungrouped = [k for k in env.keys() if k not in assigned]
    return GroupResult(groups=groups, ungrouped=ungrouped)


def to_grouped_dotenv(env: EnvFile, result: GroupResult, sep: str = "_") -> str:
    """Serialize env file with keys grouped by section comments."""
    lines: List[str] = []

    for group, keys in result.groups.items():
        lines.append(f"# [{group}]")
        for key in keys:
            value = env.get(key) or ""
            lines.append(f"{key}={value}")
        lines.append("")

    if result.ungrouped:
        lines.append("# [other]")
        for key in result.ungrouped:
            value = env.get(key) or ""
            lines.append(f"{key}={value}")

    return "\n".join(lines).strip() + "\n"
