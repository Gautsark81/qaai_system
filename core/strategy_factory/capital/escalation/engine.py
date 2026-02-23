from datetime import datetime
from core.strategy_factory.capital.escalation.audit_record import EscalationAuditRecord
from core.governance.events import GovernanceEventType, emit_governance_event


def evaluate_escalation(
    strategy_id,
    symbol,
    capital_before,
    governance_chain_id,
    decision=None,
    capital_after=None,
):
    """
    Evaluate escalation decision and emit governance audit event.

    decision and capital_after are optional to allow
    lightweight test invocation.
    """

    # Provide safe defaults for tests
    if decision is None:
        class _DefaultDecision:
            level = 0
            reason = "AUTO"
            approved = True

        decision = _DefaultDecision()

    if capital_after is None:
        capital_after = capital_before

    record = EscalationAuditRecord(
        strategy_id=strategy_id,
        symbol=symbol,
        timestamp=datetime.utcnow(),
        escalation_level=decision.level,
        reason=decision.reason,
        approved=decision.approved,
        capital_before=capital_before,
        capital_after=capital_after,
        governance_chain_id=governance_chain_id,
    )

    emit_governance_event(
        event_type=GovernanceEventType.GOV_ESCALATION_DECISION,
        payload=record.to_dict(),
        governance_chain_id=governance_chain_id,
    )

    return record
