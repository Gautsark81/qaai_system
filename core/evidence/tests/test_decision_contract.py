# core/evidence/tests/test_decision_contract.py

from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

import pytest

from core.evidence.decision_contracts import DecisionEvidence


def make_sample_evidence() -> DecisionEvidence:
    return DecisionEvidence(
        decision_id="dec-001",
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id="alpha_1",
        alpha_stream="trend",
        market_regime="TREND_LOW_VOL",
        regime_confidence=0.82,
        drift_detected=False,
        requested_weight=0.25,
        approved_weight=0.20,
        capital_available=1.0,
        ssr=0.78,
        confidence=0.91,
        risk_score=0.12,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="High SSR, stable regime, low risk",
        factors=(
            ("ssr", 0.78),
            ("confidence", 0.91),
            ("regime_score", 0.95),
        ),
        parent_decision_id=None,
        checksum="abc123",
    )


def test_decision_evidence_is_immutable():
    evidence = make_sample_evidence()

    with pytest.raises(FrozenInstanceError):
        evidence.risk_score = 0.99


def test_decision_evidence_fields_present():
    evidence = make_sample_evidence()

    assert evidence.decision_id == "dec-001"
    assert evidence.decision_type == "CAPITAL_ALLOC"
    assert evidence.strategy_id == "alpha_1"
    assert evidence.market_regime == "TREND_LOW_VOL"
    assert isinstance(evidence.factors, tuple)
    assert all(isinstance(k, str) and isinstance(v, float) for k, v in evidence.factors)

def test_decision_evidence_hashability():
    """
    Evidence must be usable in sets / as keys if needed.
    """
    evidence1 = make_sample_evidence()
    evidence2 = make_sample_evidence()

    evidence_set = {evidence1, evidence2}
    assert len(evidence_set) == 1
