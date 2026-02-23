# core/execution/authority_registry.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Set
from pathlib import Path


@dataclass(frozen=True)
class ExecutionAuthorityRegistry:
    """
    Canonical execution authority declaration.

    Defines the ONLY allowed execution root path.
    """

    allowed_root: str = "core/execution"

    def is_authorized_path(self, path: Path) -> bool:
        normalized = str(path).replace("\\", "/")
        return normalized.startswith(self.allowed_root)


def get_registry() -> ExecutionAuthorityRegistry:
    return ExecutionAuthorityRegistry()