from datetime import datetime, timedelta

from core.evidence.decision_contracts import DecisionEvidence
from core.oversight.detectors.governance_friction import GovernanceFrictionDetector


# ======================================================
# Test Factory (Canonical DecisionEvidence)
# ======================================================

def make_decision(
    *,
    decision_id: str,
    decision_type: str,
    strategy_id: str,
    timestamp: datetime,
):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type=decision_type,
        strategy_id=strategy_id,
        alpha_stream="trend",
        market_regime="TREND",
        regime_confidence=0.8,
        drift_detected=False,
        timestamp=timestamp,
        requested_weight=0.2,
        approved_weight=0.2,
        capital_available=1.0,
        ssr=0.75,
        confidence=0.85,
        risk_score=0.3,
        governance_required=True,
        governance_status="APPROVED",
        reviewer="tester",
        rationale="test decision",
        factors={},
        parent_decision_id=None,
        checksum="test-checksum",
    )


# ======================================================
# Tests
# ======================================================

def test_latency_warning_detected():
    detector = GovernanceFrictionDetector()

    decisions = [
        make_decision(
            decision_id="d1",
            decision_type="APPROVE",
            strategy_id="alpha",
            timestamp=datetime.utcnow() - timedelta(hours=30),
        )
    ]

    obs = detector.detect(
        decisions=decisions,
        detected_at=datetime.utcnow(),
    )

    assert len(obs) == 1
    assert obs[0].severity == "WARNING"


def test_latency_critical_detected():
    detector = GovernanceFrictionDetector()

    decisions = [
        make_decision(
            decision_id="d1",
            decision_type="APPROVE",
            strategy_id="alpha",
            timestamp=datetime.utcnow() - timedelta(hours=100),
        )
    ]

    obs = detector.detect(
        decisions=decisions,
        detected_at=datetime.utcnow(),
    )

    assert len(obs) == 1
    assert obs[0].severity == "CRITICAL"


def test_reversal_detected():
    detector = GovernanceFrictionDetector()

    t0 = datetime.utcnow()

    decisions = [
        make_decision(
            decision_id="d1",
            decision_type="APPROVE",
            strategy_id="alpha",
            timestamp=t0,
        ),
        make_decision(
            decision_id="d2",
            decision_type="REJECT",
            strategy_id="alpha",
            timestamp=t0 + timedelta(hours=2),
        ),
    ]

    obs = detector.detect(
        decisions=decisions,
        detected_at=t0 + timedelta(hours=3),
    )

    assert any("reversal" in o.observation_id for o in obs)
