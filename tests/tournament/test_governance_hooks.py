# tests/tournament/test_governance_hooks.py

from datetime import datetime, timezone

from core.tournament.governance_contracts import (
    GovernanceDecision,
    GovernanceStatus,
)
from core.tournament.governance_gate import filter_governance_approved
from core.tournament.promotion_artifact import PromotionArtifact


def _promo(strategy_id: str):
    return PromotionArtifact(
        run_id="run_001",
        strategy_id=strategy_id,
        promoted=True,
        reasons=[],
        metrics_version="v1",
        promotion_version="t4_v1",
        created_at=datetime.now(timezone.utc),
    )


def _decision(strategy_id: str, status: GovernanceStatus):
    return GovernanceDecision(
        run_id="run_001",
        strategy_id=strategy_id,
        status=status,
        reviewer="risk_committee",
        reasons=[],
        decided_at=datetime.now(timezone.utc),
    )


def test_only_governance_approved_strategies_pass():
    promotions = [_promo("s1"), _promo("s2"), _promo("s3")]

    decisions = [
        _decision("s1", GovernanceStatus.APPROVED),
        _decision("s2", GovernanceStatus.REJECTED),
    ]

    approved = filter_governance_approved(
        promotions=promotions,
        decisions=decisions,
    )

    ids = {p.strategy_id for p in approved}
    assert ids == {"s1"}
