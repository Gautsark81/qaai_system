import pytest
from datetime import datetime

from core.evidence.decision_store import DecisionEvidenceStore
from core.evidence.decision_contracts import DecisionEvidence


def make_evidence(
    decision_id: str,
    decision_type: str,
    parent_decision_id=None,
):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type=decision_type,
        timestamp=datetime.utcnow(),
        strategy_id="STRAT-1",
        alpha_stream=None,
        market_regime=None,
        regime_confidence=None,
        drift_detected=False,
        requested_weight=None,
        approved_weight=None,
        capital_available=None,
        ssr=None,
        confidence=None,
        risk_score=None,
        governance_required=False,
        governance_status="AUTO",
        reviewer=None,
        rationale="test",
        factors={},
        parent_decision_id=parent_decision_id,
        checksum="__AUTO__",
    )


def test_parent_decision_must_exist():
    """
    Invariant:
    A decision may reference a parent decision ONLY if
    that parent already exists in the store.
    """

    store = DecisionEvidenceStore()

    parent = make_evidence("DECISION-PARENT", "STRATEGY")
    child = make_evidence(
        "DECISION-CHILD",
        "EXECUTION",
        parent_decision_id="DECISION-PARENT",
    )

    store.append(parent)
    store.append(child)

    assert len(store.all()) == 2


def test_missing_parent_decision_is_rejected():
    """
    Invariant:
    Orphan decisions MUST NOT be allowed.
    """

    store = DecisionEvidenceStore()

    orphan = make_evidence(
        "DECISION-ORPHAN",
        "EXECUTION",
        parent_decision_id="DOES-NOT-EXIST",
    )

    with pytest.raises(ValueError, match="Parent decision not found"):
        store.append(orphan)
