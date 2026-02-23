from datetime import datetime, timezone

from core.evidence.decision_contracts import DecisionEvidence
from core.evidence.replay_engine import replay_decisions
from core.evidence.diff_engine import diff_frames


def test_deterministic_replay_and_diff():
    t1 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t2 = datetime(2026, 1, 2, tzinfo=timezone.utc)

    e1 = DecisionEvidence(
        decision_id="d1",
        decision_type="CAPITAL_ALLOC",
        timestamp=t1,
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="TREND",
        regime_confidence=0.8,
        drift_detected=False,
        requested_weight=None,
        approved_weight=0.5,
        capital_available=1.0,
        ssr=0.7,
        confidence=0.9,
        risk_score=None,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="initial",
        factors=(("ssr", 0.7),),
        parent_decision_id=None,
        checksum="c1",
    )

    e2 = DecisionEvidence(
        decision_id="d2",
        decision_type="CAPITAL_ALLOC",
        timestamp=t2,
        strategy_id="alpha_1",
        alpha_stream=None,
        market_regime="TREND",
        regime_confidence=0.85,
        drift_detected=False,
        requested_weight=None,
        approved_weight=0.8,
        capital_available=1.0,
        ssr=0.75,
        confidence=0.92,
        risk_score=None,
        governance_required=False,
        governance_status=None,
        reviewer=None,
        rationale="update",
        factors=(("ssr", 0.75),),
        parent_decision_id=None,
        checksum="c2",
    )

    frames = replay_decisions(evidence=[e1, e2])
    assert len(frames) == 2

    diff = diff_frames(before=frames[0], after=frames[1])

    assert diff.changed["capital"]["alpha_1"] == (0.5, 0.8)
