# core/dashboard_read/tests/test_snapshot_hash.py

import pytest

from core.dashboard_read.crypto.snapshot_hash import compute_snapshot_hash, SnapshotHashError


def test_same_snapshot_produces_same_hash():
    snapshot = {
        "a": 1,
        "b": {"x": 10, "y": 20},
    }

    h1 = compute_snapshot_hash(snapshot)
    h2 = compute_snapshot_hash(snapshot)

    assert h1 == h2


def test_key_order_does_not_affect_hash():
    snapshot1 = {"a": 1, "b": 2}
    snapshot2 = {"b": 2, "a": 1}

    assert compute_snapshot_hash(snapshot1) == compute_snapshot_hash(snapshot2)


def test_bit_level_change_changes_hash():
    snapshot1 = {"a": 1}
    snapshot2 = {"a": 2}

    assert compute_snapshot_hash(snapshot1) != compute_snapshot_hash(snapshot2)


def test_hash_is_hex_encoded_sha256():
    snapshot = {"a": 1}

    h = compute_snapshot_hash(snapshot)

    assert isinstance(h, str)
    assert len(h) == 64  # SHA-256 hex length
    assert all(c in "0123456789abcdef" for c in h)


def test_invalid_snapshot_raises_error():
    snapshot = {"a": set([1, 2, 3])}

    with pytest.raises(SnapshotHashError):
        compute_snapshot_hash(snapshot)
