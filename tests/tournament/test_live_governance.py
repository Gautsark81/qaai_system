from datetime import datetime, timezone

from core.tournament.live_candidate_artifact import LiveCandidateArtifact
from core.tournament.live_governance_contracts import (
    LiveGovernanceDecision,
    LiveGovernanceStatus,
)
from core.tournament.live_governance_gate import filter_live_governance_approved


def _candidate(strategy_id: str, promoted=True):
    return LiveCandidateArtifact(
        run_id="run_live_001",
        strategy_id=strategy_id,
        promoted=promoted,
        reasons=[],
        paper_version="t5_v1",
        live_promotion_version="t6_v1",
        created_at=datetime.now(timezone.utc),
    )


def _decision(strategy_id: str, status: LiveGovernanceStatus):
    return LiveGovernanceDecision(
        run_id="run_live_001",
        strategy_id=strategy_id,
        status=status,
        reviewer="risk_committee",
        reasons=[],
        decided_at=datetime.now(timezone.utc),
    )


def test_only_human_approved_strategies_pass():
    candidates = [
        _candidate("s1"),
        _candidate("s2"),
        _candidate("s3"),
    ]

    decisions = [
        _decision("s1", LiveGovernanceStatus.APPROVED),
        _decision("s2", LiveGovernanceStatus.REJECTED),
    ]

    approved = filter_live_governance_approved(
        live_candidates=candidates,
        decisions=decisions,
    )

    ids = {c.strategy_id for c in approved}
    assert ids == {"s1"}
