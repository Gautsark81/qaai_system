# core/evidence/tests/test_checksum.py

from datetime import datetime, timezone

import pytest

from core.evidence.checksum import compute_checksum


def test_checksum_is_deterministic():
    fields = [
        ("strategy_id", "alpha_1"),
        ("weight", 0.25),
        ("confidence", 0.91234),
    ]

    c1 = compute_checksum(fields=fields)
    c2 = compute_checksum(fields=fields)

    assert c1 == c2


def test_checksum_changes_on_value_change():
    fields_1 = [
        ("strategy_id", "alpha_1"),
        ("weight", 0.25),
    ]

    fields_2 = [
        ("strategy_id", "alpha_1"),
        ("weight", 0.30),
    ]

    assert compute_checksum(fields=fields_1) != compute_checksum(fields=fields_2)


def test_checksum_order_matters():
    fields_1 = [
        ("a", 1),
        ("b", 2),
    ]

    fields_2 = [
        ("b", 2),
        ("a", 1),
    ]

    assert compute_checksum(fields=fields_1) != compute_checksum(fields=fields_2)


def test_checksum_handles_none_and_bool():
    fields = [
        ("governance_required", False),
        ("reviewer", None),
    ]

    checksum = compute_checksum(fields=fields)
    assert isinstance(checksum, str)
    assert len(checksum) > 10


def test_checksum_supports_datetime():
    fields = [
        ("timestamp", datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc)),
    ]

    checksum = compute_checksum(fields=fields)
    assert isinstance(checksum, str)


def test_checksum_rejects_unsupported_types():
    fields = [
        ("bad", {"not": "allowed"}),
    ]

    with pytest.raises(TypeError):
        compute_checksum(fields=fields)
