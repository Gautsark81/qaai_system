import pytest
from datetime import datetime, timedelta

from core.evidence.drift_gap.detector import DriftGapDetector
from core.evidence.drift_gap.models import (
    DriftGapType,
    DriftSeverity,
    DriftGapRecord,
)


def test_detects_position_drift():
    detector = DriftGapDetector()

    record = detector.detect(
        expected_state={
            "position": {"NIFTY": 100},
            "capital_used": 50000,
            "orders": {},
        },
        observed_state={
            "position": {"NIFTY": 75},
            "capital_used": 50000,
            "orders": {},
        },
        as_of=datetime.utcnow(),
    )

    assert record is not None
    assert record.gap_type == DriftGapType.POSITION
    assert record.severity == DriftSeverity.WARN
    assert record.details["expected"] == 100
    assert record.details["observed"] == 75


def test_detects_capital_drift():
    detector = DriftGapDetector()

    record = detector.detect(
        expected_state={
            "position": {},
            "capital_used": 40000,
            "orders": {},
        },
        observed_state={
            "position": {},
            "capital_used": 46000,
            "orders": {},
        },
        as_of=datetime.utcnow(),
    )

    assert record.gap_type == DriftGapType.CAPITAL
    assert record.severity == DriftSeverity.WARN


def test_detects_order_state_drift():
    detector = DriftGapDetector()

    record = detector.detect(
        expected_state={
            "position": {},
            "capital_used": 0,
            "orders": {"ORD1": "FILLED"},
        },
        observed_state={
            "position": {},
            "capital_used": 0,
            "orders": {"ORD1": "OPEN"},
        },
        as_of=datetime.utcnow(),
    )

    assert record.gap_type == DriftGapType.ORDER_STATE
    assert record.severity == DriftSeverity.INFO


def test_no_drift_returns_none():
    detector = DriftGapDetector()

    record = detector.detect(
        expected_state={
            "position": {"NIFTY": 50},
            "capital_used": 25000,
            "orders": {"ORD1": "FILLED"},
        },
        observed_state={
            "position": {"NIFTY": 50},
            "capital_used": 25000,
            "orders": {"ORD1": "FILLED"},
        },
        as_of=datetime.utcnow(),
    )

    assert record is None


def test_drift_record_is_immutable():
    detector = DriftGapDetector()

    record = detector.detect(
        expected_state={
            "position": {"BANKNIFTY": 25},
            "capital_used": 30000,
            "orders": {},
        },
        observed_state={
            "position": {"BANKNIFTY": 0},
            "capital_used": 30000,
            "orders": {},
        },
        as_of=datetime.utcnow(),
    )

    with pytest.raises(AttributeError):
        record.severity = DriftSeverity.CRITICAL
