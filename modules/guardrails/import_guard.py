# modules/guardrails/import_guard.py

import sys
from types import ModuleType
from typing import Iterable


class ImportBlocker(ModuleType):
    def __init__(self, blocked_prefixes: Iterable[str]):
        super().__init__("import_blocker")
        self._blocked = tuple(blocked_prefixes)

    def __getattr__(self, name):
        raise ImportError("Access to this module is blocked by guardrails")


def install_import_block(blocked_prefixes: Iterable[str]) -> None:
    for prefix in blocked_prefixes:
        sys.modules[prefix] = ImportBlocker(blocked_prefixes)
