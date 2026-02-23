import pytest
from datetime import datetime, timezone

from core.capital.arming.contracts import (
    CapitalArmingState,
    CapitalArmingDecision,
)
from core.capital.arming.ledger import CapitalArmingLedger
from core.capital.arming.gate import CapitalArmingGate


def _decision(state: CapitalArmingState, allowed: bool = True):
    return CapitalArmingDecision(
        state=state,
        allowed=allowed,
        reasons=[state.value],
        decided_at=datetime.now(tz=timezone.utc),
    )


def test_blocks_when_no_arming_decisions():
    ledger = CapitalArmingLedger()
    gate = CapitalArmingGate(ledger=ledger)

    assert gate.is_capital_allowed() is False


def test_allows_when_latest_state_allows():
    ledger = CapitalArmingLedger()
    ledger.append(_decision(CapitalArmingState.PAPER))

    gate = CapitalArmingGate(ledger=ledger)

    assert gate.is_capital_allowed() is True


def test_blocks_when_latest_state_is_disarmed():
    ledger = CapitalArmingLedger()
    ledger.append(_decision(CapitalArmingState.SHADOW))
    ledger.append(_decision(CapitalArmingState.DISARMED, allowed=False))

    gate = CapitalArmingGate(ledger=ledger)

    assert gate.is_capital_allowed() is False


def test_gate_is_read_only():
    ledger = CapitalArmingLedger()
    gate = CapitalArmingGate(ledger=ledger)

    with pytest.raises(AttributeError):
        gate.append  # type: ignore[attr-defined]
