from datetime import datetime, timezone

from core.governance.drift.governance_drift_detector import (
    GovernanceDriftDetector,
)


# ---------------------------------------------------------------------
# Minimal Dummy Ledger + Entry Models (Test-Scoped)
# ---------------------------------------------------------------------


class DummyScalingEntry:
    def __init__(
        self,
        *,
        strategy_id,
        previous_capital,
        new_capital,
        scale_factor,
        governance_id,
        timestamp,
    ):
        self.strategy_id = strategy_id
        self.previous_capital = previous_capital
        self.new_capital = new_capital
        self.scale_factor = scale_factor
        self.governance_id = governance_id
        self.timestamp = timestamp


class DummyThrottleEntry:
    def __init__(
        self,
        *,
        strategy_id,
        throttle_level,
        governance_id,
        timestamp,
    ):
        self.strategy_id = strategy_id
        self.throttle_level = throttle_level
        self.governance_id = governance_id
        self.timestamp = timestamp


class DummyLedger:
    def __init__(self):
        self.entries = []

    def append(self, entry):
        self.entries.append(entry)


# ---------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------


def test_valid_governance_chain_has_no_drift():
    gov_id = "gov-valid"
    ts = datetime.now(timezone.utc)

    scaling = DummyLedger()
    throttle = DummyLedger()

    scaling.append(
        DummyScalingEntry(
            strategy_id="STRAT-1",
            previous_capital=1_000_000,
            new_capital=1_200_000,
            scale_factor=1.2,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    throttle.append(
        DummyThrottleEntry(
            strategy_id="STRAT-1",
            throttle_level=1.0,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    detector = GovernanceDriftDetector(
        scaling_ledger=scaling,
        throttle_ledger=throttle,
    )

    report = detector.detect(governance_id=gov_id)

    assert report.valid
    assert report.errors == ()


# ---------------------------------------------------------------------


def test_orphan_scaling_detected():
    gov_id = "gov-orphan-scaling"
    ts = datetime.now(timezone.utc)

    scaling = DummyLedger()
    throttle = DummyLedger()

    scaling.append(
        DummyScalingEntry(
            strategy_id="STRAT-1",
            previous_capital=1_000_000,
            new_capital=1_200_000,
            scale_factor=1.2,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    detector = GovernanceDriftDetector(
        scaling_ledger=scaling,
        throttle_ledger=throttle,
    )

    report = detector.detect(governance_id=gov_id)

    assert not report.valid
    assert "THROTTLE_MISSING" in report.errors


# ---------------------------------------------------------------------


def test_capital_continuity_violation_detected():
    gov_id = "gov-continuity"
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 2, tzinfo=timezone.utc)

    scaling = DummyLedger()
    throttle = DummyLedger()

    scaling.append(
        DummyScalingEntry(
            strategy_id="STRAT-1",
            previous_capital=1_000_000,
            new_capital=1_200_000,
            scale_factor=1.2,
            governance_id=gov_id,
            timestamp=t1,
        )
    )

    # Broken continuity
    scaling.append(
        DummyScalingEntry(
            strategy_id="STRAT-1",
            previous_capital=900_000,  # ❌ should be 1_200_000
            new_capital=950_000,
            scale_factor=0.8,
            governance_id=gov_id,
            timestamp=t2,
        )
    )

    detector = GovernanceDriftDetector(
        scaling_ledger=scaling,
        throttle_ledger=throttle,
    )

    report = detector.detect(governance_id=gov_id)

    assert not report.valid
    assert "CAPITAL_CONTINUITY_VIOLATION" in report.errors


# ---------------------------------------------------------------------


def test_cross_strategy_collision_detected():
    gov_id = "gov-collision"
    ts = datetime.now(timezone.utc)

    scaling = DummyLedger()
    throttle = DummyLedger()

    scaling.append(
        DummyScalingEntry(
            strategy_id="STRAT-A",
            previous_capital=1_000_000,
            new_capital=1_100_000,
            scale_factor=1.1,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    throttle.append(
        DummyThrottleEntry(
            strategy_id="STRAT-B",  # ❌ different strategy
            throttle_level=1.0,
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    detector = GovernanceDriftDetector(
        scaling_ledger=scaling,
        throttle_ledger=throttle,
    )

    report = detector.detect(governance_id=gov_id)

    assert not report.valid
    assert "CROSS_STRATEGY_COLLISION" in report.errors


# ---------------------------------------------------------------------


def test_throttle_scale_conflict_detected():
    gov_id = "gov-conflict"
    ts = datetime.now(timezone.utc)

    scaling = DummyLedger()
    throttle = DummyLedger()

    scaling.append(
        DummyScalingEntry(
            strategy_id="STRAT-1",
            previous_capital=1_000_000,
            new_capital=1_200_000,
            scale_factor=1.2,  # Scale up
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    throttle.append(
        DummyThrottleEntry(
            strategy_id="STRAT-1",
            throttle_level=0.5,  # Throttled
            governance_id=gov_id,
            timestamp=ts,
        )
    )

    detector = GovernanceDriftDetector(
        scaling_ledger=scaling,
        throttle_ledger=throttle,
    )

    report = detector.detect(governance_id=gov_id)

    assert not report.valid
    assert "THROTTLE_SCALE_CONFLICT" in report.errors