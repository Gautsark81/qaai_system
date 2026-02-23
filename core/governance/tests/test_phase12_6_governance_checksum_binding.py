from datetime import datetime, timezone

import pytest

from core.governance.checksum.governance_checksum_engine import (
    GovernanceChecksumEngine,
)


def test_checksum_is_deterministic():
    engine = GovernanceChecksumEngine()

    ts = datetime(2026, 1, 1, tzinfo=timezone.utc)

    c1 = engine.compute(
        governance_id="gov-001",
        scaling_checksum="scale-abc",
        throttle_checksum="thr-xyz",
        promotion_checksum="promo-123",
        timestamp=ts,
    )

    c2 = engine.compute(
        governance_id="gov-001",
        scaling_checksum="scale-abc",
        throttle_checksum="thr-xyz",
        promotion_checksum="promo-123",
        timestamp=ts,
    )

    assert c1.checksum == c2.checksum


def test_checksum_changes_if_any_component_changes():
    engine = GovernanceChecksumEngine()
    ts = datetime.now(timezone.utc)

    base = engine.compute(
        governance_id="gov-001",
        scaling_checksum="scale",
        throttle_checksum="thr",
        promotion_checksum=None,
        timestamp=ts,
    )

    changed = engine.compute(
        governance_id="gov-001",
        scaling_checksum="scale-CHANGED",
        throttle_checksum="thr",
        promotion_checksum=None,
        timestamp=ts,
    )

    assert base.checksum != changed.checksum


def test_missing_governance_id_raises():
    engine = GovernanceChecksumEngine()
    ts = datetime.now(timezone.utc)

    with pytest.raises(ValueError):
        engine.compute(
            governance_id="",
            scaling_checksum=None,
            throttle_checksum=None,
            promotion_checksum=None,
            timestamp=ts,
        )