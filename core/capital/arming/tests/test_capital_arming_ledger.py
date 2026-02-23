import pytest
from datetime import datetime, timezone

from core.capital.arming.contracts import (
    CapitalArmingState,
    CapitalArmingDecision,
)
from core.capital.arming.ledger import CapitalArmingLedger


def _decision(state: CapitalArmingState):
    return CapitalArmingDecision(
        state=state,
        allowed=True,
        reasons=[state.value],
        decided_at=datetime.now(tz=timezone.utc),
    )


def test_append_and_retrieve_history():
    ledger = CapitalArmingLedger()

    d1 = _decision(CapitalArmingState.SHADOW)
    d2 = _decision(CapitalArmingState.PAPER)

    ledger.append(d1)
    ledger.append(d2)

    history = ledger.history()

    assert history == [d1, d2]


def test_ledger_is_append_only():
    ledger = CapitalArmingLedger()
    d1 = _decision(CapitalArmingState.SHADOW)

    ledger.append(d1)

    with pytest.raises(RuntimeError):
        ledger._records.clear()


def test_history_is_immutable_copy():
    ledger = CapitalArmingLedger()
    d1 = _decision(CapitalArmingState.SHADOW)

    ledger.append(d1)

    history = ledger.history()
    history.append(d1)

    assert ledger.history() == [d1]
