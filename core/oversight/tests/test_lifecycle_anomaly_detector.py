from datetime import datetime

from core.oversight.detectors.lifecycle_anomaly import (
    StrategyLifecycleAnomalyDetector,
)
from core.strategy_factory.registry import StrategyRecord
from core.strategy_factory.spec import StrategySpec


def make_record(
    *,
    dna: str,
    state: str,
    history=None,
    ssr=None,
    confidence=None,
):
    """
    Create a minimal, VALID StrategyRecord for oversight tests.
    Must conform to StrategySpec exactly.
    """

    # ✅ Canonical StrategySpec (minimal but valid)
    spec = StrategySpec(
        name="test_strategy",
        alpha_stream="trend",
        timeframe="5m",
        universe=["NIFTY"],   # ✅ REQUIRED field
        params={},
    )

    record = StrategyRecord(dna=dna, spec=spec)
    record.state = state
    record.history = history or []

    if ssr is not None:
        record.ssr = ssr
    if confidence is not None:
        record.confidence = confidence

    return record


def test_lifecycle_oscillation_detected():
    detector = StrategyLifecycleAnomalyDetector()

    record = make_record(
        dna="alpha",
        state="PAPER",
        history=[
            {"from": "GENERATED", "to": "BACKTESTED"},
            {"from": "BACKTESTED", "to": "PAPER"},
            {"from": "PAPER", "to": "BACKTESTED"},
        ],
    )

    observations = detector.detect(
        records=[record],
        detected_at=datetime.utcnow(),
    )

    assert observations
    assert observations[0].severity == "WARNING"
    assert "oscillation" in observations[0].observation_id


def test_blocked_strong_strategy_detected():
    detector = StrategyLifecycleAnomalyDetector()

    record = make_record(
        dna="alpha",
        state="PAPER",
        ssr=0.9,
        confidence=0.9,
    )

    observations = detector.detect(
        records=[record],
        detected_at=datetime.utcnow(),
    )

    assert observations
    assert "blocked" in observations[0].observation_id


def test_no_false_positive_for_live_strategy():
    detector = StrategyLifecycleAnomalyDetector()

    record = make_record(
        dna="alpha",
        state="LIVE",
        ssr=0.9,
        confidence=0.9,
    )

    observations = detector.detect(
        records=[record],
        detected_at=datetime.utcnow(),
    )

    assert observations == []
