# core/compliance/bundle/bundle.py
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
class ImmutableAuditBundle:
    """
    Fully sealed audit bundle.
    """
    bundle_hash: str
    payload: Dict[str, Any]


class AuditBundleBuilder:
    """
    Builds a deterministic, immutable audit bundle.
    """

    def build(
        self,
        *,
        exports: Dict[str, Any],
        provenance: Dict[str, Any],
        snapshot_seal: Dict[str, Any],
    ) -> ImmutableAuditBundle:
        payload = {
            "exports": exports,
            "provenance": provenance,
            "snapshot_seal": snapshot_seal,
        }

        canonical = _canonical_bytes(payload)
        bundle_hash = hashlib.sha256(canonical).hexdigest()

        return ImmutableAuditBundle(
            bundle_hash=bundle_hash,
            payload=payload,
        )
