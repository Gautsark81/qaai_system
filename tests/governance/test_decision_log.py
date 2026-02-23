from modules.governance.decision_log import (
    GovernanceDecision,
    GovernanceDecisionLog,
)
from datetime import datetime


def test_decision_logged():
    log = GovernanceDecisionLog()
    event = GovernanceDecision(
        strategy_id="s1",
        decision="APPROVED",
        actor="admin",
        timestamp=datetime.utcnow(),
        reason="Passed all checks",
    )

    log.record(event)

    assert len(log.all()) == 1
