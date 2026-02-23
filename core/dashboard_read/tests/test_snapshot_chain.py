# core/dashboard_read/tests/test_snapshot_chain.py

import pytest

from core.dashboard_read.crypto.chain import (
    compute_chain_hash,
    compute_chain_from_snapshots,
    GENESIS_CHAIN_HASH,
)
from core.dashboard_read.crypto.errors import ChainVerificationError


def test_chain_is_deterministic():
    snapshot = {"a": 1}

    first = compute_chain_hash(
        snapshot_hash="a" * 64,
        previous_chain_hash=GENESIS_CHAIN_HASH,
    )
    second = compute_chain_hash(
        snapshot_hash="a" * 64,
        previous_chain_hash=GENESIS_CHAIN_HASH,
    )

    assert first == second


def test_chain_changes_if_snapshot_hash_changes():
    c1 = compute_chain_hash("a" * 64, GENESIS_CHAIN_HASH)
    c2 = compute_chain_hash("b" * 64, GENESIS_CHAIN_HASH)

    assert c1 != c2


def test_chain_changes_if_previous_hash_changes():
    c1 = compute_chain_hash("a" * 64, GENESIS_CHAIN_HASH)
    c2 = compute_chain_hash("a" * 64, "1" * 64)

    assert c1 != c2


def test_full_chain_from_snapshots():
    snapshots = [
        {"a": 1},
        {"a": 2},
        {"a": 3},
    ]

    chain = compute_chain_from_snapshots(snapshots)

    assert len(chain) == 3
    assert chain[0] != chain[1]
    assert chain[1] != chain[2]


def test_reordering_snapshots_changes_chain():
    s1 = [{"a": 1}, {"a": 2}]
    s2 = [{"a": 2}, {"a": 1}]

    assert compute_chain_from_snapshots(s1) != compute_chain_from_snapshots(s2)


def test_invalid_hash_rejected():
    with pytest.raises(ChainVerificationError):
        compute_chain_hash("invalid", GENESIS_CHAIN_HASH)
