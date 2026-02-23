# core/dashboard_read/tests/test_canonical_serializer.py

import pytest

from core.dashboard_read.canonical.serializer import canonicalize_snapshot
from core.dashboard_read.canonical.errors import CanonicalizationError


def test_deterministic_output_for_same_snapshot():
    snapshot = {
        "b": 2,
        "a": 1,
        "nested": {"y": 20, "x": 10},
    }

    first = canonicalize_snapshot(snapshot)
    second = canonicalize_snapshot(snapshot)

    assert first == second


def test_key_order_does_not_affect_output():
    snapshot1 = {"a": 1, "b": 2}
    snapshot2 = {"b": 2, "a": 1}

    assert canonicalize_snapshot(snapshot1) == canonicalize_snapshot(snapshot2)


def test_float_normalization_is_stable():
    snapshot = {"value": 0.30000000000000004}

    result = canonicalize_snapshot(snapshot)

    assert b"0.3" in result


def test_none_is_preserved():
    snapshot = {"value": None}

    result = canonicalize_snapshot(snapshot)

    assert b'"value":null' in result


def test_tuple_and_list_equivalence():
    snapshot_list = {"values": [1, 2, 3]}
    snapshot_tuple = {"values": (1, 2, 3)}

    assert canonicalize_snapshot(snapshot_list) == canonicalize_snapshot(snapshot_tuple)


def test_rejects_non_string_keys():
    snapshot = {1: "invalid"}

    with pytest.raises(CanonicalizationError):
        canonicalize_snapshot(snapshot)


def test_rejects_unsupported_types():
    snapshot = {"value": set([1, 2, 3])}

    with pytest.raises(CanonicalizationError):
        canonicalize_snapshot(snapshot)


def test_schema_version_is_embedded():
    snapshot = {"a": 1}

    result = canonicalize_snapshot(snapshot)

    assert b"_canonical_schema_version" in result
