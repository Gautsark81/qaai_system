# core/evidence/tests/test_decision_evidence_checksum.py

from datetime import datetime, timedelta
from core.evidence.decision_contracts import DecisionEvidence


def make_base_evidence(**overrides):
    base = dict(
        decision_id="DEC-1",
        decision_type="CAPITAL_ALLOC",
        strategy_id="alpha_1",
        alpha_stream="mean_reversion",
        market_regime="trend",
        regime_confidence=0.85,
        drift_detected=False,
        requested_weight=0.3,
        approved_weight=0.25,
        capital_available=1_000_000,
        ssr=0.78,
        confidence=0.91,
        risk_score=0.12,
        governance_required=False,
        governance_status="auto",
        reviewer=None,
        rationale="Stable allocation",
        factors={"volatility": 0.2, "liquidity": 0.9},
        parent_decision_id=None,
        timestamp=datetime.utcnow(),
        checksum="__AUTO__",  # placeholder
    )
    base.update(overrides)
    return DecisionEvidence(**base)


def test_checksum_is_deterministic():
    e1 = make_base_evidence()
    e2 = make_base_evidence()

    assert e1.checksum == e2.checksum


def test_checksum_ignores_timestamp():
    e1 = make_base_evidence(timestamp=datetime.utcnow())
    e2 = make_base_evidence(timestamp=datetime.utcnow() + timedelta(days=1))

    assert e1.checksum == e2.checksum


def test_checksum_changes_on_semantic_change():
    e1 = make_base_evidence(approved_weight=0.25)
    e2 = make_base_evidence(approved_weight=0.30)

    assert e1.checksum != e2.checksum


def test_checksum_is_order_invariant_for_factors():
    e1 = make_base_evidence(factors={"a": 1, "b": 2})
    e2 = make_base_evidence(factors={"b": 2, "a": 1})

    assert e1.checksum == e2.checksum


def test_checksum_is_hex_string():
    e = make_base_evidence()
    assert isinstance(e.checksum, str)
    assert len(e.checksum) >= 32
    int(e.checksum, 16)  # must be valid hex
