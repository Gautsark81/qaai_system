# core/compliance/notary/snapshot.py
import json
import hashlib
from dataclasses import dataclass
from typing import Any, Dict


def _canonical_bytes(payload: Dict[str, Any]) -> bytes:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


@dataclass(frozen=True)
class SnapshotSeal:
    """
    Cryptographic seal for an audit snapshot.
    """
    digest: str
    algorithm: str = "sha256"


class SnapshotNotary:
    """
    Deterministically notarizes an audit snapshot.

    NOTE:
    - No timestamps
    - No UUIDs
    - No external services
    """

    def notarize(self, *, snapshot: Dict[str, Any]) -> SnapshotSeal:
        canonical = _canonical_bytes(snapshot)
        digest = hashlib.sha256(canonical).hexdigest()
        return SnapshotSeal(digest=digest)
