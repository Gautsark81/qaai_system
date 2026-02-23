import pytest
from unittest.mock import patch
from datetime import datetime, timezone

from core.strategy_factory.capital.escalation.audit_record import EscalationAuditRecord
from core.governance.events import GovernanceEventType


# -------------------------------------------------------------------
# EscalationAuditRecord Immutability
# -------------------------------------------------------------------

def test_escalation_audit_record_is_immutable():
    record = EscalationAuditRecord(
        strategy_id="STRAT1",
        symbol="NIFTY",
        timestamp=datetime.now(timezone.utc),
        escalation_level="LEVEL_1",
        reason="Threshold reached",
        approved=True,
        capital_before=100000.0,
        capital_after=150000.0,
        governance_chain_id="CHAIN_ABC",
    )

    # Dataclass should be frozen / immutable
    with pytest.raises((AttributeError, TypeError)):
        record.strategy_id = "MODIFIED"


# -------------------------------------------------------------------
# Governance Emission Binding
# -------------------------------------------------------------------

def test_escalation_emits_governance_event():
    with patch("core.governance.events.emit_governance_event") as mock_emit:

        from core.strategy_factory.capital.escalation.engine import evaluate_escalation

        record = evaluate_escalation(
            strategy_id="STRAT1",
            symbol="NIFTY",
            capital_before=100000.0,
            governance_chain_id="CHAIN_TEST",
        )

        # Ensure event emitted exactly once
        mock_emit.assert_called_once()

        _, kwargs = mock_emit.call_args

        # Validate event type
        assert kwargs["event_type"] == GovernanceEventType.GOV_ESCALATION_DECISION

        # Validate governance chain id
        assert kwargs["governance_chain_id"] == "CHAIN_TEST"

        # Validate payload integrity
        payload = kwargs["payload"]

        assert payload["strategy_id"] == "STRAT1"
        assert payload["symbol"] == "NIFTY"
        assert payload["capital_before"] == 100000.0
        assert payload["capital_after"] == 100000.0
        assert payload["governance_chain_id"] == "CHAIN_TEST"

        # Ensure function returned a proper record
        assert isinstance(record, EscalationAuditRecord)


# -------------------------------------------------------------------
# to_dict Contract Validation
# -------------------------------------------------------------------

def test_escalation_audit_record_to_dict():
    ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    record = EscalationAuditRecord(
        strategy_id="STRAT2",
        symbol="BANKNIFTY",
        timestamp=ts,
        escalation_level="LEVEL_2",
        reason="Performance sustained",
        approved=False,
        capital_before=200000.0,
        capital_after=200000.0,
        governance_chain_id="CHAIN_XYZ",
    )

    data = record.to_dict()

    assert data == {
        "strategy_id": "STRAT2",
        "symbol": "BANKNIFTY",
        "timestamp": ts.isoformat(),
        "escalation_level": "LEVEL_2",
        "reason": "Performance sustained",
        "approved": False,
        "capital_before": 200000.0,
        "capital_after": 200000.0,
        "governance_chain_id": "CHAIN_XYZ",
    }
