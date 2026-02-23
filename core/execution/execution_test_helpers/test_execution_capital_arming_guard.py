import pytest

from core.capital.arming.contracts import CapitalArmingState
from core.capital.arming.ledger import CapitalArmingLedger
from core.capital.arming.contracts import CapitalArmingDecision
from core.execution.capital_arming_guard import (
    ExecutionCapitalArmingGuard,
    CapitalArmingEnforcementError,
)
from datetime import datetime, timezone


def _decision(state: CapitalArmingState, allowed: bool):
    return CapitalArmingDecision(
        state=state,
        allowed=allowed,
        reasons=[state.value],
        decided_at=datetime.now(tz=timezone.utc),
    )


def test_blocks_execution_when_capital_not_armed():
    ledger = CapitalArmingLedger()
    ledger.append(_decision(CapitalArmingState.DISARMED, allowed=False))

    guard = ExecutionCapitalArmingGuard(ledger=ledger)

    with pytest.raises(CapitalArmingEnforcementError):
        guard.enforce()


def test_allows_execution_when_capital_armed():
    ledger = CapitalArmingLedger()
    ledger.append(_decision(CapitalArmingState.PAPER, allowed=True))

    guard = ExecutionCapitalArmingGuard(ledger=ledger)

    guard.enforce()  # should not raise


def test_blocks_when_no_arming_history():
    ledger = CapitalArmingLedger()

    guard = ExecutionCapitalArmingGuard(ledger=ledger)

    with pytest.raises(CapitalArmingEnforcementError):
        guard.enforce()
