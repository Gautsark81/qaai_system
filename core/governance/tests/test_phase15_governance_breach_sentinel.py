from datetime import datetime, timedelta, timezone

from core.governance.sentinel.governance_breach_sentinel import (
    GovernanceBreachSentinel,
)
from core.governance.escalation.governance_strike_ledger import (
    GovernanceStrikeLedger,
)
from core.governance.escalation.governance_escalation_engine import (
    EscalationDecision,
)


def _zero_capital_decision(governance_id: str, ts: datetime):
    """
    Helper to construct a valid EscalationDecision
    using your real escalation contract.
    """
    return EscalationDecision(
        governance_id=governance_id,
        strike_count=3,
        escalation_level="CRITICAL",
        throttle_override=None,
        freeze_capital=False,
        zero_capital=True,
        explanation="AUTO_ZERO_CAPITAL",
        timestamp=ts,
    )


def test_breach_on_repeated_zero_capital():
    now = datetime.now(timezone.utc)

    history = [
        _zero_capital_decision("gov-1", now - timedelta(hours=1)),
        _zero_capital_decision("gov-1", now - timedelta(hours=2)),
    ]

    ledger = GovernanceStrikeLedger()
    sentinel = GovernanceBreachSentinel()

    result = sentinel.evaluate(
        governance_id="gov-1",
        escalation_history=history,
        strike_ledger=ledger,
        now=now,
    )

    assert result.breached is True
    assert result.reason == "REPEATED_ZERO_CAPITAL_ESCALATION"


def test_breach_on_strike_limit():
    ledger = GovernanceStrikeLedger()

    for _ in range(10):
        ledger.add_strike("gov-2", reason="TEST")

    sentinel = GovernanceBreachSentinel()

    result = sentinel.evaluate(
        governance_id="gov-2",
        escalation_history=[],
        strike_ledger=ledger,
    )

    assert result.breached is True
    assert result.reason == "STRIKE_LIMIT_EXCEEDED"


def test_no_breach_when_safe():
    ledger = GovernanceStrikeLedger()
    ledger.add_strike("gov-3", reason="MINOR")

    sentinel = GovernanceBreachSentinel()

    result = sentinel.evaluate(
        governance_id="gov-3",
        escalation_history=[],
        strike_ledger=ledger,
    )

    assert result.breached is False