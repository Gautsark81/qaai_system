# core/strategy_factory/capital/escalation/replay_verifier.py

from core.strategy_factory.capital.escalation.audit_record import EscalationAuditRecord


class EscalationReplayMismatch(Exception):
    """Raised when replayed escalation does not match audit record."""


class EscalationReplayVerifier:
    """
    Replays an escalation decision using recorded inputs
    and verifies deterministic equivalence.
    """

    def __init__(self, escalation_engine):
        self._engine = escalation_engine

    def verify(self, record: EscalationAuditRecord):
        """
        Re-run escalation logic in replay mode and ensure outcome matches.
        """

        replay_decision = self._engine.evaluate_escalation(
            strategy_id=record.strategy_id,
            symbol=record.symbol,
            capital_before=record.capital_before,
            governance_chain_id=record.governance_chain_id,
            replay_mode=True,  # must disable emission
        )

        if replay_decision.approved != record.approved:
            raise EscalationReplayMismatch(
                "Replay approval mismatch"
            )

        if replay_decision.level != record.escalation_level:
            raise EscalationReplayMismatch(
                "Replay level mismatch"
            )

        if replay_decision.reason != record.reason:
            raise EscalationReplayMismatch(
                "Replay reason mismatch"
            )

        return True