from datetime import datetime, timezone
import copy

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.audit_timeline import build_audit_timeline


def _decision(decision_id: str):
    return DecisionEvidence(
        decision_id=decision_id,
        decision_type="CAPITAL_ALLOC",
        timestamp=datetime.now(timezone.utc),
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime=None,
        regime_confidence=None,
        drift_detected=False,
        requested_weight=None,
        approved_weight=0.5,
        capital_available=1.0,
        ssr=0.8,
        confidence=0.9,
        risk_score=None,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="test",
        factors=(),
        parent_decision_id=None,
        checksum=f"chk-{decision_id}",
    )


def test_audit_timeline_is_pure_and_non_mutating():
    """
    Phase 12.5A.1-T3

    Invariants:
    - build_audit_timeline does NOT mutate input evidence
    - Returned timeline is independent
    - No enrichment or inference occurs
    """

    d1 = _decision("D1")
    d2 = _decision("D2")

    evidence = [d1, d2]

    # Deep copy to detect mutation
    snapshot = copy.deepcopy(evidence)

    timeline = build_audit_timeline(evidence)

    # Input evidence must be unchanged
    assert evidence == snapshot

    # Timeline must be a new object
    assert timeline is not evidence

    # Timeline entries must be distinct objects
    assert timeline[0] is not evidence[0]
    assert timeline[1] is not evidence[1]

    # Semantic identity must match
    assert timeline[0].decision_id == "D1"
    assert timeline[1].decision_id == "D2"
