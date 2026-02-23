# core/runtime/release_lock.py
import hashlib
import os
from pathlib import Path


class ReleaseLock:
    """
    Prevents code mutation after deployment.
    """

    def __init__(self, root: Path, expected_hash: str):
        self.root = root
        self.expected_hash = expected_hash

    def _compute_hash(self) -> str:
        h = hashlib.sha256()
        for p in sorted(self.root.rglob("*.py")):
            h.update(p.read_bytes())
        return h.hexdigest()

    def verify(self) -> None:
        actual = self._compute_hash()
        if actual != self.expected_hash:
            raise RuntimeError("Release lock violated")
