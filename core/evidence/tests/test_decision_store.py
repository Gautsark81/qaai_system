# core/evidence/tests/test_decision_store.py

from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.decision_store import DecisionEvidenceStore


def make_evidence(decision_id: str, strategy_id: str) -> DecisionEvidence:
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id=strategy_id,
        alpha_stream="trend",
        market_regime="RANGE_LOW_VOL",
        regime_confidence=0.6,
        drift_detected=False,
        requested_weight=0.15,
        approved_weight=0.10,
        capital_available=1.0,
        ssr=0.65,
        confidence=0.7,
        risk_score=0.3,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="Moderate confidence allocation",
        factors={"ssr": 0.65},
        parent_decision_id=None,
        checksum=f"chk-{decision_id}",
    )


def test_store_append_and_read_all():
    store = DecisionEvidenceStore()

    e1 = make_evidence("d1", "alpha_1")
    e2 = make_evidence("d2", "alpha_2")

    store.append(e1)
    store.append(e2)

    all_records = store.all()

    assert len(all_records) == 2
    assert all_records[0] == e1
    assert all_records[1] == e2


def test_store_is_append_only():
    store = DecisionEvidenceStore()
    e1 = make_evidence("d1", "alpha_1")

    store.append(e1)
    records = store.all()

    # Ensure returned collection cannot mutate internal state
    assert isinstance(records, tuple)


def test_filter_by_strategy():
    store = DecisionEvidenceStore()

    store.append(make_evidence("d1", "alpha_1"))
    store.append(make_evidence("d2", "alpha_2"))
    store.append(make_evidence("d3", "alpha_1"))

    alpha_1_records = store.by_strategy("alpha_1")

    assert len(alpha_1_records) == 2
    assert all(e.strategy_id == "alpha_1" for e in alpha_1_records)


def test_filter_by_decision_type():
    store = DecisionEvidenceStore()

    store.append(make_evidence("d1", "alpha_1"))
    store.append(make_evidence("d2", "alpha_2"))

    capital_decisions = store.by_type("CAPITAL_ALLOC")

    assert len(capital_decisions) == 2
