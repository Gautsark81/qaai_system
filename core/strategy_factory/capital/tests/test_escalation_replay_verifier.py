# core/strategy_factory/capital/tests/test_escalation_replay_verifier.py

from datetime import datetime

from core.strategy_factory.capital.escalation.audit_record import EscalationAuditRecord
from core.strategy_factory.capital.escalation.replay_verifier import (
    EscalationReplayVerifier,
)


class DummyDecision:
    def __init__(self, approved, level, reason):
        self.approved = approved
        self.level = level
        self.reason = reason


class DummyEngine:
    def evaluate_escalation(
        self,
        strategy_id,
        symbol,
        capital_before,
        governance_chain_id,
        replay_mode=False,
    ):
        return DummyDecision(
            approved=True,
            level="LEVEL_1",
            reason="Threshold reached",
        )


def test_escalation_replay_success():
    engine = DummyEngine()
    verifier = EscalationReplayVerifier(engine)

    record = EscalationAuditRecord(
        strategy_id="STRAT1",
        symbol="NIFTY",
        timestamp=datetime.utcnow(),
        escalation_level="LEVEL_1",
        reason="Threshold reached",
        approved=True,
        capital_before=100000.0,
        capital_after=150000.0,
        governance_chain_id="CHAIN_ABC",
    )

    assert verifier.verify(record) is True

def test_escalation_replay_detects_mismatch():
    class BadEngine(DummyEngine):
        def evaluate_escalation(self, *args, **kwargs):
            return DummyDecision(
                approved=False,
                level="LEVEL_1",
                reason="Threshold reached",
            )

    engine = BadEngine()
    verifier = EscalationReplayVerifier(engine)

    record = EscalationAuditRecord(
        strategy_id="STRAT1",
        symbol="NIFTY",
        timestamp=datetime.utcnow(),
        escalation_level="LEVEL_1",
        reason="Threshold reached",
        approved=True,
        capital_before=100000.0,
        capital_after=150000.0,
        governance_chain_id="CHAIN_ABC",
    )

    import pytest

    with pytest.raises(Exception):
        verifier.verify(record)

