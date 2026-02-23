# core/dashboard_read/crypto/chain.py

from __future__ import annotations

import hashlib
from typing import Iterable, List

from core.dashboard_read.crypto.snapshot_hash import compute_snapshot_hash
from core.dashboard_read.crypto.errors import ChainVerificationError


GENESIS_CHAIN_HASH = "0" * 64


def compute_chain_hash(
    snapshot_hash: str,
    previous_chain_hash: str,
) -> str:

    _validate_hash(snapshot_hash, "snapshot_hash")
    _validate_hash(previous_chain_hash, "previous_chain_hash")

    material = previous_chain_hash + snapshot_hash
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def compute_chain_from_snapshots(
    snapshots: Iterable[dict],
) -> List[str]:

    chain: List[str] = []
    previous = GENESIS_CHAIN_HASH

    for snapshot in snapshots:
        snapshot_hash = compute_snapshot_hash(snapshot)
        current = compute_chain_hash(snapshot_hash, previous)
        chain.append(current)
        previous = current

    return chain


def _validate_hash(value: str, name: str) -> None:
    if not isinstance(value, str):
        raise ChainVerificationError(f"{name} must be a string")

    if len(value) != 64:
        raise ChainVerificationError(f"{name} must be 64 hex characters")

    if any(c not in "0123456789abcdef" for c in value):
        raise ChainVerificationError(f"{name} must be lowercase hex")